# Thiết kế mục tiêu: FMCG Workflow Simulator

**Trạng thái:** Accepted; cấu trúc nền đã được triển khai  
**Phạm vi:** Kiến trúc mục tiêu; các miền ngoài purchase vẫn chưa triển khai  
**Hệ thống đích đầu tiên:** Odoo 19 qua JSON-2 API

## 1. Mục tiêu

Simulator đóng vai nhân viên và các tác nhân nghiệp vụ của công ty FMCG. Mỗi lần được
kích hoạt, master entrypoint quan sát trạng thái các hệ thống nguồn, quyết định thao tác
nào hợp lý tại thời điểm đó, tạo hoặc tiếp tục scenario, rồi gọi API của hệ thống đích.

Ví dụ:

- tồn kho nguyên liệu dự kiến thấp hơn mức tối thiểu → lập RFQ;
- nguyên liệu đã về và có nhu cầu thành phẩm → phát hành lệnh sản xuất;
- có thành phẩm và nhu cầu bán → tạo đơn bán hoặc giao dịch POS;
- hóa đơn đến hạn → thực hiện bước thanh toán;
- cơ hội CRM đủ điều kiện → chuyển thành báo giá.

Thiết kế phải hỗ trợ chạy local bằng một process và chuyển sang Airflow mà không thay đổi
logic nghiệp vụ. Các workflow phải có quan hệ nhân quả, có thể truy vết, tái lập bằng seed,
và không tạo trùng khi scheduler retry hoặc API mất response.

## 2. Ranh giới trách nhiệm

```text
Airflow / internal loop / CLI
          │ kích hoạt + scheduled_at + run_id
          ▼
      Application Master
          │
          ├── Observe ──► Collectors ──► Odoo / POS / DMS / ...
          │                  │
          │                  ▼
          │             Business Snapshot
          │
          ├── Decide ───► Policies ────► Decision proposals
          │
          ├── Plan ─────► Scenario Planner + guards
          │                  │
          │                  ▼
          │             Durable State Store
          │
          └── Execute ──► Workflow Runtime ──► System Adapters
                                                │
                                                ▼
                                         Business systems
```

Scheduler chỉ quyết định **khi nào gọi**. Simulator quyết định **tại thời điểm đó nên làm
gì**. Odoo quyết định thao tác có hợp lệ theo rule, quyền và cấu hình ERP hay không.

Phiên bản đầu chưa có state store riêng và dùng chứng từ Odoo làm nguồn trạng thái.
State store chỉ được bổ sung khi có workflow dài hạn hoặc liên hệ nhiều hệ thống mà trạng
thái không thể suy ra an toàn từ Odoo. Khi đó không dùng Airflow metadata database làm
state nghiệp vụ vì retry task và trạng thái nghiệp vụ là hai khái niệm khác nhau.

## 3. Một lần chạy của master

Master cung cấp một use case duy nhất cho scheduler:

```text
run_once(scheduled_at, trigger_id)
    1. đọc cấu hình và kiểm tra các dependency cần thiết
    2. thu thập snapshot từ Odoo
    3. chạy các policy được bật để tạo decision proposal
    4. kiểm tra chứng từ/scenario tương ứng đang tồn tại trong Odoo
    5. thực hiện hoặc đối soát thao tác theo correlation ID
    6. tìm các chứng từ mô phỏng đang đến hạn và tiếp tục workflow
    7. xuất execution summary và kết thúc
```

`run_once` không chứa rule mua hàng hoặc model Odoo. Nó chỉ điều phối
các port của application. Lệnh `run` local chỉ gọi lặp lại chính use case này; nó không
có một scheduler nghiệp vụ thứ hai.

Thứ tự mặc định là quyết định trước rồi thực thi. Một scenario vừa tạo có thể được thực
thi trong cùng invocation nếu step đầu đã đến hạn. Có thể cấu hình giới hạn thời gian,
số decision và số step mỗi invocation để tránh một lần chạy chiếm tài nguyên quá lâu.

## 4. Cấu trúc code base đề xuất

Giai đoạn đầu dùng một package phẳng. Mỗi file có một trách nhiệm chính nhưng chưa tạo
folder theo layer hoặc domain khi mới chỉ có một vài luồng nghiệp vụ.

```text
services/data-source-simulators/workflow-simulator/
├── README.md
├── config/
│   └── simulator.example.yaml
├── deployment/
│   └── docker-compose.simulator.yaml
├── src/workflow_simulator/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── master.py
│   ├── policies.py
│   ├── workflows.py
│   └── odoo.py
└── tests/
    ├── test_master.py
    ├── test_policies.py
    ├── test_workflows.py
    ├── test_odoo.py
    └── test_store.py
```

Trách nhiệm của từng file:

| File | Trách nhiệm |
|---|---|
| `main.py` | CLI, `run-once`, vòng lặp local và composition root |
| `config.py` | Đọc và kiểm tra runtime/policy/scenario config |
| `models.py` | Dataclass, enum và các contract dữ liệu dùng chung |
| `master.py` | Điều phối observe → decide → plan → execute |
| `policies.py` | Các rule ra quyết định thuần, bắt đầu bằng replenishment |
| `workflows.py` | Scenario definition, step handler và workflow runtime |
| `odoo.py` | JSON-2 client, collector và thao tác nghiệp vụ Odoo |

Không tạo `utils.py`, `common.py` hoặc `helpers.py`. Logic phải nằm cạnh trách nhiệm mà
nó phục vụ. Các contract nhỏ có thể đặt trong file sử dụng chúng; `models.py` chỉ chứa
kiểu dữ liệu thật sự được nhiều file chia sẻ.

### Khi nào mới tách thành folder

Chỉ tách khi có bằng chứng code đã lớn, không dựa trên nhu cầu dự kiến. Một file được cân
nhắc tách khi có ít nhất một trong các dấu hiệu:

- chứa từ ba miền nghiệp vụ độc lập trở lên;
- thay đổi thường xuyên bởi các lý do khác nhau;
- test file tương ứng trở nên khó tìm hoặc cần nhiều fixture riêng;
- có từ hai implementation thật của cùng contract;
- import vòng hoặc tên class phải thêm tiền tố miền để phân biệt;
- một developer khó đọc trọn trách nhiệm của file trong một lần review.

Ví dụ đường phát triển tự nhiên:

```text
policies.py                         policies/
├── ReplenishmentPolicy            ├── __init__.py
├── ProductionPolicy       ───►     ├── replenishment.py
└── SalesDemandPolicy              ├── production.py
                                    └── sales.py

odoo.py                             adapters/odoo/
├── Json2Client                    ├── client.py
├── OdooCollector          ───►     ├── collector.py
└── OdooGateway                    └── gateways/
```

Việc tách folder là di chuyển cơ học quanh các contract đã có. Master không đổi hành vi.

## 5. Quy tắc phụ thuộc

```text
main ──► master ──► policies
  │         │           │
  │         ├────► workflows
  │         │
  └────► odoo ◄──── models
```

- `policies.py` không import `odoo.py`, `store.py`, Airflow hoặc framework CLI.
- `master.py` nhận dependency qua constructor, không tự tạo client/database.
- `odoo.py` không chứa rule quyết định khi nào cần mua hoặc sản xuất.
- `main.py` là nơi duy nhất nối config, collector, policy và runtime.
- Workflow của một miền không gọi trực tiếp workflow của miền khác. Quan hệ giữa chúng
  được biểu diễn qua decision, event hoặc precondition đọc từ snapshot.

Đây là ranh giới logic trong các file phẳng, chưa cần áp dụng đầy đủ folder theo Clean
Architecture. Khi tách folder, hướng phụ thuộc này được giữ nguyên.

## 6. Các contract cốt lõi

Các đoạn dưới là pseudocode để chốt trách nhiệm, không phải mã triển khai.

```python
class SimulationMaster:
    def run_once(command: RunCommand) -> RunSummary: ...

class SnapshotCollector:
    def collect(request: ObservationRequest) -> BusinessSnapshot: ...

class DecisionPolicy:
    name: str
    def evaluate(snapshot: BusinessSnapshot, context: DecisionContext) -> list[Decision]: ...

class ScenarioPlanner:
    def plan(decision: Decision, context: PlanningContext) -> ScenarioPlan: ...

class WorkflowRuntime:
    def process_due(now, limit) -> ExecutionSummary: ...

class StateStore:
    def register_invocation(trigger_id, scheduled_at) -> InvocationRegistration: ...
    def create_scenario_if_absent(plan, decision_key) -> CreateResult: ...
    def find_open_scenarios(subject_key, scenario_type) -> list[Scenario]: ...
    def claim_due_steps(now, limit, lease) -> list[ClaimedStep]: ...
    def record_write_intent(step_id, idempotency_key) -> None: ...
    def complete_step(step_id, result, next_steps) -> None: ...
    def defer_step(step_id, retry_at, error) -> None: ...
    def block_step(step_id, reason) -> None: ...

class TargetGateway:
    def inspect(operation) -> ExternalObservation: ...
    def execute(operation) -> ExternalResult: ...
    def reconcile(operation, idempotency_key) -> ReconciliationResult: ...
```

các contract cần cho phiên bản đầu có thể là `Protocol` hoặc class nhỏ nằm trong
`master.py` và `workflows.py`. Chưa cần tạo một file `ports.py` cho tới khi nhiều adapter
cùng sử dụng và việc đặt contract cạnh consumer không còn rõ ràng.

`DecisionPolicy` là pure domain logic: cùng snapshot, config, seed và thời điểm sẽ cho
cùng quyết định. Random generator được truyền vào context và seed được lưu, không gọi
random toàn cục.

## 7. Business Snapshot

Snapshot là mô hình đọc tối thiểu phục vụ quyết định, không phải bản sao toàn bộ Odoo.
Mỗi policy khai báo dữ liệu cần thiết để collector có thể batch các truy vấn.

Ví dụ snapshot cho replenishment:

```text
MaterialPosition
├── company_id
├── warehouse_id
├── product_id
├── on_hand_qty
├── reserved_qty
├── confirmed_incoming_qty
├── draft_rfq_qty
├── manufacturing_demand_qty
├── sales_demand_qty
├── reorder_min_qty
├── reorder_target_qty
├── uom_id
└── observed_at
```

Policy mua hàng dùng một công thức được cấu hình và version hóa, ví dụ:

```text
projected_qty = on_hand_qty
              - reserved_qty
              + confirmed_incoming_qty
              - manufacturing_demand_qty

net_requirement = max(0, reorder_target_qty
                          - projected_qty
                          - draft_rfq_qty)
```

Công thức thật phải được xác nhận với cách Odoo định nghĩa forecasted quantity và phạm
vi warehouse/location. Không cộng hoặc trừ hai chỉ số đã bao hàm nhau. Snapshot lưu
`observed_at`, nguồn và phiên bản mapping để có thể giải thích một quyết định cũ.

Không yêu cầu transaction phân tán khi đọc nhiều hệ thống. Mỗi phần snapshot ghi thời
điểm đọc; policy có thể từ chối quyết định nếu dữ liệu quá cũ hoặc không đầy đủ.

## 8. Decision, scenario và workflow

Ba khái niệm phải tách biệt:

| Khái niệm | Ý nghĩa | Ví dụ |
|---|---|---|
| Decision | Kết luận từ trạng thái hiện tại | Cần mua 80 kg nguyên liệu A |
| Scenario | Một phiên nghiệp vụ tồn tại qua nhiều lần chạy | Chu kỳ mua A ngày 05/09 |
| Step | Một hành động hoặc lần đối soát | Tạo RFQ, xác nhận PO, nhận hàng |

Decision đề xuất phải chứa:

```text
decision_type, decision_key, policy_name, policy_version,
subject_keys, observed_facts, reason, proposed_payload,
scheduled_at, seed, expires_at
```

`decision_key` chống việc cùng một invocation/policy tạo lặp một đề xuất. Nó không được
dùng thay cho guard nghiệp vụ. Trước khi tạo scenario mua, planner vẫn phải kiểm tra:

- có scenario replenishment đang mở cho company/warehouse/product hay không;
- lượng RFQ, PO và incoming hiện tại đã đáp ứng thiếu hụt chưa;
- giới hạn số scenario và ngân sách giả lập;
- decision có hết hạn do snapshot cũ hay không.

Workflow purchase mục tiêu:

```text
planned
  → create_rfq
  → wait_before_confirm
  → confirm_purchase
  → wait_for_receipt_date
  → receive_goods
  → create_vendor_bill
  → post_vendor_bill
  → wait_until_due
  → register_payment
  → completed
```

Mỗi step định nghĩa `precondition`, `execute`, `postcondition`, `reconcile`, retry policy
và timeout policy. `execute` không được tự đổi step tiếp theo nếu postcondition chưa được
quan sát. `to approve`, backorder wizard, lot/expiry, partial receipt và payment matching
là các nhánh trạng thái nghiệp vụ, không được coi là lỗi HTTP đơn thuần.

## 9. Quyết định của master tại một thời điểm

Policy registry chứa các policy được bật và thứ tự ưu tiên. Ví dụ:

```text
P10  reconcile_unknown_writes
P20  progress_open_purchase_workflows
P30  prevent_raw_material_stockout
P40  release_manufacturing_order
P50  generate_sales_demand
P60  generate_pos_demand
P70  progress_finance_workflows
P80  progress_crm_workflows
```

Độ ưu tiên giúp capacity được dùng cho thao tác bảo toàn tính nhất quán trước khi sinh
nhu cầu mới. Runtime vẫn đối soát và tiến các workflow đã mở ngay cả khi bước observe
cho policy mới thất bại, miễn dữ liệu cần cho step đó còn đọc được.

Master không hard-code chuỗi `nếu thiếu kho thì gọi purchase.py`. Policy trả về decision
đã định kiểu; planner registry ánh xạ decision type sang scenario definition.

## 10. State store tương lai và mô hình dữ liệu

Mục này chưa áp dụng cho phiên bản stateless hiện tại. Chỉ triển khai khi Odoo không còn
đủ để biểu diễn và đối soát trạng thái workflow.

Các bảng logic tối thiểu:

```text
simulation_invocation
  trigger_id UNIQUE, scheduled_at, started_at, finished_at, status, summary

decision_record
  decision_key UNIQUE, policy, policy_version, observed_facts,
  proposed_payload, reason, created_at, scenario_id

scenario
  scenario_id, scenario_type, status, subject_key, correlation_id,
  config_version, seed, created_at, completed_at

scenario_step
  step_id, scenario_id, step_type, status, due_at, attempt,
  lease_owner, lease_until, input_payload, output_payload, last_error

external_operation
  operation_id, step_id, target_system, operation_type,
  idempotency_key, status, external_model, external_id,
  intent_recorded_at, dispatched_at, reconciled_at

state_transition
  transition_id, entity_type, entity_id, from_state, to_state,
  reason, occurred_at, invocation_id
```

Payload lưu trong state phải tránh credential và dữ liệu cá nhân không cần thiết.
Transition history là append-only; record hiện hành có thể update để truy vấn nhanh.

SQLite adapter dùng cho local/single runner. PostgreSQL adapter dùng transaction,
`SELECT ... FOR UPDATE SKIP LOCKED` hoặc cơ chế claim tương đương khi có nhiều worker.
Hai adapter phải vượt cùng contract test suite.

## 11. Idempotency và lỗi không rõ kết quả

Mỗi thao tác ghi có một `idempotency_key` ổn định, được lưu trước khi gọi hệ thống đích:

```text
<environment>:<scenario_id>:<step_type>:<step_version>
```

State machine kỹ thuật của một step ghi:

```text
ready → intent_recorded → dispatched → verifying → succeeded
                         ↘ outcome_unknown → reconciling ─┘
                                                    ↘ blocked
```

Không tự replay write khi timeout nếu hệ thống đích có thể đã commit. Gateway phải tìm
theo correlation/idempotency key và kiểm tra postcondition trước. Với Odoo, dùng `origin`
chỉ là giải pháp MVP vì không có unique constraint. Trước khi chạy nhiều replica, cần một
endpoint/module Odoo cung cấp idempotency key unique và thực hiện atomic create-or-return.

Retry của Airflow chạy lại cùng `trigger_id` và `scheduled_at`; invocation registration
trả về record cũ. Retry cấp application áp dụng cho lỗi đọc hoặc lỗi chắc chắn chưa gửi.
Retry thao tác ghi tuân theo policy riêng của step và luôn đi qua reconciliation.

## 12. Tích hợp Airflow

Hai entrypoint giữ cùng contract:

```text
Local loop: mỗi N giây → run_once(now, locally-derived-trigger-id)
Airflow:    theo DAG      → run_once(data_interval_end, dag_run/logical trigger id)
```

CLI mục tiêu:

```text
simulator run-once --scheduled-at <UTC timestamp> --trigger-id <stable id>
simulator run-local --poll-interval 5
simulator inspect --scenario-id <id>
simulator reconcile --scenario-id <id> --dry-run
```

Airflow đặt `catchup=False` cho chế độ không tạo bù, `max_active_runs=1` cho tới khi
idempotency phía Odoo đủ mạnh, và truyền logical time thay vì để simulator tự đọc wall clock cho việc sinh
decision. Wall clock vẫn dùng cho timeout, lease và telemetry.

Khi workflow cần state store và chuyển sang distributed executor:

1. bổ sung `PostgresStore` theo contract ở mục 10;
2. giữ nguyên policy và Odoo gateway;
3. bổ sung claim/lease cho nhiều worker;
4. chỉ tăng concurrency sau khi idempotency phía Odoo đủ mạnh.

Không tạo DAG cho từng PO hoặc từng step nghiệp vụ. Một DAG kích hoạt application;
scenario runtime chịu trách nhiệm với tiến trình dài hạn và nhánh nghiệp vụ.

## 13. Cấu hình

Cấu hình chia ba nhóm:

- **runtime:** batch size, lease, timeout, retry, store DSN, target connection name;
- **policy:** threshold, target stock, probability, seasonality, capacity, enabled flag;
- **scenario:** thời gian chờ, actor, warehouse, company, approval behavior, step version.

Credential chỉ đi qua secret/environment mechanism. ID Odoo không nên rải trực tiếp
trong rule; cấu hình tham chiếu business key/external ID khi có thể, bootstrap resolver
chuyển thành internal ID và cache kèm target/database/company.

Mỗi scenario lưu `config_version`, `policy_version` và seed lúc tạo. Thay cấu hình không
làm thay đổi ngầm các scenario đang chạy; migration hoặc policy version mới quyết định
cách xử lý chúng.

## 14. Observability và vận hành

Mỗi log/metric cần các correlation field phù hợp:

```text
invocation_id, scenario_id, step_id, decision_key,
target_system, external_model, external_id, company_id
```

Không log API key, Authorization header hoặc response body chưa lọc. Metrics tối thiểu:

- invocation duration và status;
- decision proposed/accepted/rejected theo policy và reason;
- active/blocked scenario theo type;
- step success/failure/reconciliation duration;
- target API latency/error;
- snapshot age;
- business counters như RFQ quantity và stockout avoided.

Blocked scenario cần công cụ inspect và reconciliation dry-run. Việc resume thủ công phải
ghi actor, lý do và transition; không xử lý bằng cách xóa state database.

## 15. Chiến lược kiểm thử

- **Unit:** policy với snapshot cố định; planner; state transition; deterministic seed.
- **Contract:** mọi `StateStore`; JSON-2 request/response; gateway mapping.
- **Scenario:** luồng nhiều invocation, delay, partial receipt, approval, stale snapshot.
- **Failure:** timeout trước/sau commit, restart ở từng write state, duplicate trigger,
  concurrent claim, rate limit, dữ liệu Odoo bị thay đổi ngoài simulator.
- **Integration:** Odoo disposable database với master data cố định; xác minh chứng từ và
  tác động kho/kế toán qua public API hoặc ORM test phù hợp.
- **Architecture:** kiểm tra `policies.py` không phụ thuộc Odoo/store/framework và master
  không tự khởi tạo adapter.

Test không dùng sleep thật. Clock, ID generator và random source được inject để kiểm soát.

## 16. Lộ trình chuyển từ code hiện tại

Thiết kế này chưa yêu cầu thay đổi production code. Khi triển khai, tiến hành theo các
vertical slice có thể kiểm thử:

1. Giữ package phẳng; đổi CLI hiện tại thành `main.py` và dùng nó làm composition root.
2. Tách `Engine.tick()` thành các phương thức `observe`, `decide/plan` và `execute_due`
   trong các file phẳng tương ứng, giữ hành vi RFQ cũ.
3. Bổ sung `scheduled_at`/`trigger_id` và invocation idempotency cho `run-once`.
4. Chuyển rule tạo RFQ theo slot thành `InventoryReplenishmentPolicy` dựa trên snapshot.
5. Chuyển purchase flow hiện tại sang scenario/step runtime và giữ test timeout/restart.
6. Hoàn thiện receipt → bill → payment theo một vertical slice end-to-end.
7. Thêm manufacturing rồi sales/POS/CRM theo dependency nghiệp vụ.
8. Tách folder theo miền/adapter chỉ khi đạt tiêu chí ở mục 4; không tách toàn bộ một lần.
9. Thêm PostgreSQL implementation và Airflow DAG sau khi contract của master ổn định.
10. Thêm Odoo-side atomic idempotency trước khi chạy nhiều replica.

Trong giai đoạn chuyển tiếp, chỉ một cơ chế được phép sinh cùng loại nghiệp vụ: cron addon
Odoo cũ, local simulator hoặc Airflow. Việc bật song song có thể tạo dữ liệu trùng.

## 17. Tiêu chí chấp nhận kiến trúc

Thiết kế được coi là đạt khi:

- thêm một policy mới không cần sửa master;
- thêm một workflow mới không cần sửa adapter của workflow khác;
- thay SQLite bằng PostgreSQL không đổi domain/application;
- thay local loop bằng Airflow không đổi policy/workflow;
- retry cùng trigger không sinh thêm decision/scenario;
- timeout sau commit không gây replay mù;
- mỗi chứng từ mô phỏng truy được về decision, facts, policy version và scenario;
- có thể giải thích tại sao hệ thống tạo hoặc không tạo RFQ tại một thời điểm;
- các giới hạn capacity và dữ liệu thiếu làm giảm tải an toàn thay vì tạo backlog vô hạn.

## 18. Điểm cần xác nhận trước khi triển khai

Các quyết định sau cần chốt bằng business rule hoặc spike trên Odoo thật:

1. Công thức tồn kho dự kiến và phạm vi location/warehouse cho từng nguyên liệu.
2. Có tính draft RFQ vào nguồn cung dự kiến hay chỉ PO đã xác nhận.
3. Nguồn nhu cầu sản xuất: forecast simulator, sales demand, MPS hay MO thực tế.
4. Quy tắc gom nhiều nguyên liệu/vendor vào một RFQ.
5. Chính sách approval, partial receipt, backorder, lot/expiry và quality check.
6. Cách tạo payment và accounting impact phù hợp cấu hình localization.
7. Nhịp mô phỏng, seasonality, tỷ lệ lỗi/hủy và time compression.
8. Ranh giới giữa POS thật của Odoo và một hệ thống POS ngoài được simulator điều phối.

Các điểm này thay đổi policy/workflow configuration và adapter mapping, không làm thay
đổi cấu trúc tổng thể ở trên.
