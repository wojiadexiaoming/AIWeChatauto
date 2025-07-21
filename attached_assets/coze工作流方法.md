执行工作流
执行已发布的工作流。​
接口说明​
此接口为非流式响应模式，对于支持流式输出的节点，应使用接口执行工作流（流式响应）获取流式响应。调用接口后，你可以从响应中获得 debug_url，访问链接即可通过可视化界面查看工作流的试运行过程，其中包含每个执行节点的输入输出等详细信息，帮助你在线调试或排障。​
扣子个人进阶版、团队版、企业版和专业版用户调用此接口时，支持通过 is_async 参数异步运行工作流，适用于工作流执行耗时较长，导致运行超时的情况。异步运行后可通过本接口返回的 execute_id 调用查询工作流异步执行结果API 获取工作流的执行结果。​
限制说明​
​
 限制项​
 说明 ​
工作流发布状态​
 必须为已发布。执行未发布的工作流会返回错误码 4200。 创建并发布工作流的操作可参考使用工作流。​
节点限制​
工作流中不能包含消息节点、开启了流式输出的结束节点、问答节点。​
关联智能体​
调用此 API 之前，应先在扣子平台中试运行此工作流，如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定智能体ID。通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。​
请求大小上限​
 20 MB，包括输入参数及运行期间产生的消息历史等所有相关数据。 ​
超时时间 ​
未开启工作流异步运行时，工作流整体超时时间为 10 分钟，建议执行时间控制在 5 分钟以内，否则不保障执行结果的准确性。 详细说明可参考工作流使用限制。​
开启工作流异步运行后，工作流整体超时时间为 24 小时。​
​
基础信息​
​
请求方式​
POST​
请求地址​
​
https://api.coze.cn/v1/workflow/run​
​
权限​
run​
确保调用该接口使用的个人令牌开通了 run 权限，详细信息参考鉴权方式。​
接口说明​
执行已发布的工作流。​
​
请求参数​
Header​
​
参数​
取值​
说明​
Authorization​
Bearer $Access_Token​
用于验证客户端身份的访问令牌。你可以在扣子平台中生成访问令牌，详细信息，参考准备工作。​
Content-Type​
application/json​
解释请求正文的方式。​
​
Body​
​
参数​
类型​
是否必选​
示例​
说明​
workflow_id​
String​
必选​
73664689170551*****​
待执行的 Workflow ID，此工作流应已发布。​
进入 Workflow 编排页面，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如 https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***，Workflow ID 为 73505836754923***。​
parameters​
String​
可选​
{​
"user_id":"12345",​
"user_name":"George"​
}​
工作流开始节点的输入参数及取值，你可以在指定工作流的编排页面查看参数列表。​
如果工作流输入参数为 Image 等类型的文件，可以调用上传文件 API 获取 file_id，在调用此 API 时，在 parameters 中以序列化之后的 JSON 格式传入 file_id。例如 “parameters” : { "input": "{\"file_id\": \"xxxxx\"}" }。​
bot_id​
String​
可选​
73428668*****​
需要关联的智能体 ID。 部分工作流执行时需要指定关联的智能体，例如存在数据库节点、变量节点等节点的工作流。​
​
​​

图片​
​
进入智能体的开发页面，开发页面 URL 中 bot 参数后的数字就是智能体t ID。例如 https://www.coze.com/space/341****/bot/73428668*****，智能体 ID 为 73428668*****。​
确保调用该接口使用的令牌开通了此智能体所在空间的权限。​
确保该智能体已发布为 API 服务。​
​
ext​
JSON Map​
可选​
​
用于指定一些额外的字段，以 Map[String][String] 格式传入。例如某些插件 会隐式用到的经纬度等字段。​
目前仅支持以下字段：​
latitude：String 类型，表示经度。​
longitude：String 类型，表示纬度。​
user_id：String 类型，表示用户 ID。​
is_async​
Boolean​
可选​
true​
是否异步运行。异步运行后可通过本接口返回的 execute_id 调用查询工作流异步执行结果API 获取工作流的最终执行结果。​
true：异步运行。​
false：（默认）同步运行。​
异步运行的参数 is_async 仅限扣子个人进阶版、团队版、企业版和专业版使用，否则调用此接口会报错 6003 Workflow execution with is_async=true is a premium feature available only to Coze Professional users。​
​
app_id​
String​
可选​
749081945898306****​
该工作流关联的应用的 ID​
​
返回参数​
​
参数​
类型​
示例​
说明​
code​
Long​
0​
调用状态码。​
0 表示调用成功。​
其他值表示调用失败。你可以通过 msg 字段判断详细的错误原因。​
msg​
String​
Success​
状态信息。API 调用失败时可通过此字段查看详细错误信息。​
data​
String​
​
工作流执行结果，通常为 JSON 序列化字符串，部分场景下可能返回非 JSON 结构的字符串。​
execute_id​
String​
741364789030728****​
异步执行的事件 ID。​
token​
Long​
​
预留字段，无需关注。​
cost​
String​
0​
预留字段，无需关注。​
debug_url​
String​
https://www.coze.cn/work_flow?execute_id=741364789030728****&space_id=736142423532160****&workflow_id=738958910358870****​
工作流试运行调试页面。访问此页面可查看每个工作流节点的运行结果、输入输出等信息。​
detail​
Object of ResponseDetail​
​
返回的详情。​
​
ResponseDetail​
​
参数​
类型​
示例​
说明​
logid​
String​
20241210152726467C48D89D6DB2****​
本次请求的日志 ID。如果遇到异常报错场景，且反复重试仍然报错，可以根据此 logid 及错误码联系扣子团队获取帮助。详细说明可参考获取帮助和技术支持。​
​
示例​
请求示例​
​
curl --location --request POST 'https://api.coze.cn/v1/workflow/run' \​
--header 'Authorization: Bearer pat_hfwkehfncaf****' \​
--header 'Content-Type: application/json' \​
--data-raw '{​
    "workflow_id": "73664689170551*****",​
    "parameters": {​
        "user_id":"12345",​
        "user_name":"George"​
    }​
}'​
​
​
返回示例​
​同步执行工作流

{​
    "code": 0,​
    "cost": "0",​
    "data": "{\"output\":\"北京的经度为116.4074°E，纬度为39.9042°N。\"}",​
    "debug_url": "https://www.coze.cn/work_flow?execute_id=741364789030728****&space_id=736142423532160****&workflow_id=738958910358870****",​
    "msg": "Success",​
    "token": 98​
}

异步执行工作流
{
    "code": 0,
    "debug_url": "https://www.coze.cn/work_flow?execute_id=742482313128840****&space_id=731375784444321****&workflow_id=74243949454920****",
    "execute_id": "74248231312884****",
    "msg": "Success"
}
执行工作流（流式响应）
执行已发布的工作流，响应方式为流式响应。​
接口说明​
调用 API 执行工作流时，对于支持流式输出的工作流，往往需要使用流式响应方式接收响应数据，例如实时展示工作流的输出信息、呈现打字机效果等。​
在流式响应中，服务端不会一次性发送所有数据，而是以数据流的形式逐条发送数据给客户端，数据流中包含工作流执行过程中触发的各种事件（event），直至处理完毕或处理中断。处理结束后，服务端会通过 event: Done 事件提示工作流执行完毕。各个事件的说明可参考​返回结果。​
目前支持流式响应的工作流节点包括输出节点、问答节点和开启了流式输出的结束节点。对于不包含这些节点的工作流，可以使用​执行工作流接口一次性接收响应数据。​
​
限制说明​
通过 API 方式执行工作流前，应确认此工作流已发布，执行从未发布过的工作流时会返回错误码 4200。创建并发布工作流的操作可参考​使用工作流。​
调用此 API 之前，应先在扣子平台中试运行此工作流。​
如果试运行时需要关联智能体，则调用此 API 执行工作流时，也需要指定 bot_id。通常情况下，执行存在数据库节点、变量节点等节点的工作流需要关联智能体。​
执行应用中的工作流时，需要指定 app_id。​
请勿同时指定 bot_id 和 app_id，否则 API 会报错 4000，表示请求参数错误。​
此接口为同步接口，如果工作流整体或某些节点运行超时，智能体可能无法提供符合预期的回复，建议将工作流的执行时间控制在 5 分钟以内。同步执行时，工作流整体超时时间限制可参考​工作流使用限制。​
工作流支持的请求大小上限为 20MB，包括输入参数以及运行期间产生的消息历史等所有相关数据。​
基础信息​
​
请求方式​
POST​
请求地址​
​
https://api.coze.cn/v1/workflow/stream_run​
​
权限​
run​
确保调用该接口使用的个人令牌开通了 run 权限，详细信息参考​鉴权方式概述。​
接口说明​
执行已发布的工作流，响应方式为流式响应。​
​
Header​
​
参数​
取值​
说明​
Authorization​
Bearer $Access_Token​
用于验证客户端身份的访问令牌。你可以在扣子平台中生成访问令牌，详细信息，参考​准备工作。​
Content-Type​
application/json​
解释请求正文的方式。​
​
​
​
Body​
​
参数​
类型​
是否必选​
说明​
workflow_id​
String ​
必选​
待执行的 Workflow ID，此工作流应已发布。​
进入 Workflow 编排页面，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如 https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***，Workflow ID 为 73505836754923***。​
parameters​
map[String]Any​
可选​
工作流开始节点的输入参数及取值，你可以在指定工作流的编排页面查看参数列表。​
如果工作流输入参数为 Image 等类型的文件，可以调用​上传文件 API 获取 file_id，在调用此 API 时在 parameters 中以序列化之后的 JSON 格式传入 file_id。例如 “parameters” : { "input": "{\"file_id\": \"xxxxx\"}" }。​
bot_id​
​
String ​
​
可选​
​
需要关联的智能体ID。 部分工作流执行时需要指定关联的智能体，例如存在数据库节点、变量节点等节点的工作流。​
​
​​

图片​
​
进入智能体的开发页面，开发页面 URL 中 bot 参数后的数字就是智能体ID。例如 https://www.coze.com/space/341****/bot/73428668*****，Bot ID 为 73428668*****。 ​
确保调用该接口使用的令牌开通了此智能体所在空间的权限。​
确保该智能体已发布为 API 服务。​
​
ext​
Map[String][String]​
​
可选​
用于指定一些额外的字段，以 Map[String][String] 格式传入。例如某些插件 会隐式用到的经纬度等字段。​
目前仅支持以下字段：​
atitude：String 类型，表示经度。​
longitude：String 类型，表示纬度。​
user_id：Integer 类型，表示用户 ID。​
app_id​
String​
可选​
工作流所在的应用 ID。​
你可以通过应用的业务编排页面 URL 中获取应用 ID，也就是 URL 中 project-ide 参数后的一串字符，例如 https://www.coze.cn/space/739174157340921****/project-ide/743996105122521****/workflow/744102227704147**** 中，应用的 ID 为 743996105122521****。​
仅运行扣子应用中的工作流时，才需要设置 app_id。智能体绑定的工作流、空间资源库中的工作流无需设置 app_id。​
​
​
返回结果​
​
在流式响应中，开发者需要注意是否存在丢包现象。​
事件 ID（id）默认从 0 开始计数，以包含 event: Done 的事件为结束标志。开发者应根据 id 确认响应消息整体无丢包现象。​
Message 事件的消息 ID 默认从 0 开始计数，以包含 node_is_finish : true 的事件为结束标志。开发者应根据 node_seq_id 确认 Message 事件中每条消息均完整返回，无丢包现象。​
​
​
参数名​
参数类型​
参数描述​
id​
Integer​
此消息在接口响应中的事件 ID。以 0 为开始。​
event​
String ​
当前流式返回的数据包事件。包括以下类型：​
Message：工作流节点输出消息，例如消息节点、结束节点的输出消息。可以在 data 中查看具体的消息内容。​
Error：报错。可以在 data 中查看 error_code 和 error_message，排查问题。​
Done：结束。表示工作流执行结束，此时 data 中包含 debug URL。​
Interrupt：中断。表示工作流中断，此时 data 字段中包含具体的中断信息。​
PING：心跳信号。表示工作流执行中，消息内容为空，用于维持连接。​
data​
Object​
事件内容。各个 event 类型的事件内容格式不同。​
​
Message 事件​
Message 事件中，data 的结构如下：​
​
参数名​
参数类型​
参数描述​
content​
String ​
流式输出的消息内容。​
node_title​
String​
输出消息的节点名称，例如消息节点、结束节点。​
node_seq_id​
String​
此消息在节点中的消息 ID，从 0 开始计数，例如消息节点的第 5 条消息。​
node_is_finish​
Boolean​
当前消息是否为此节点的最后一个数据包。​
ext​
Map[String]String​
额外字段。​
cost​
String ​
预留字段，无需关注。​
​
Interrupt 事件​
Interrupt 事件中，data 的结构如下：​
​
参数名​
参数类型​
参数描述​
interrupt_data​
Object​
中断控制内容。​
interrupt_data.event_id​
String​
工作流中断事件 ID，恢复运行时应回传此字段，具体请参见​恢复运行工作流。​
interrupt_data.type​
Integer​
工作流中断类型，恢复运行时应回传此字段，具体请参见​恢复运行工作流。​
node_title​
String​
输出消息的节点名称，例如“问答”。​
​
Error 事件​
Error 事件中，data 的结构如下：​
​
参数名​
参数类型​
参数描述​
error_code​
Integer​
调用状态码。 ​
0 表示调用成功。 ​
其他值表示调用失败。你可以通过 error_message 字段判断详细的错误原因。​
error_message​
String ​
状态信息。API 调用失败时可通过此字段查看详细错误信息。​
​
​
​
示例​
请求示例​
​
curl --location --request POST 'https://api.coze.cn/v1/workflow/stream_run' \​
--header 'Authorization: Bearer pat_fhwefweuk****' \​
--header 'Content-Type: application/json' \​
--data-raw '{​
    "workflow_id": "73664689170551*****",​
    "parameters": {​
        "user_id":"12345",​
        "user_name":"George"​
    }​
}'
Message 事件
id: 0
event: Message
data: {"content":"msg","node_is_finish":false,"node_seq_id":"0","node_title":"Message"}

id: 1
event: Message
data: {"content":"为","node_is_finish":false,"node_seq_id":"1","node_title":"Message"}

id: 2
event: Message
data: {"content":"什么小明要带一把尺子去看电影？\n因","node_is_finish":false,"node_seq_id":"2","node_title":"Message"}

id: 3
event: Message
data: {"content":"为他听说电影很长，怕","node_is_finish":false,"node_seq_id":"3","node_title":"Message"}

id: 4
event: Message
data: {"content":"坐不下！","node_is_finish":true,"node_seq_id":"4","node_title":"Message"}

id: 5
event: Message
data: {"content":"{\"output\":\"为什么小明要带一把尺子去看电影？\\n因为他听说电影很长，怕坐不下！\"}","cost":"0.00","node_is_finish":true,"node_seq_id":"0","node_title":"","token":0}

id: 6
event: Done
data: {}

Error 事件
id: 0
event: Error
data: {"error_code":4000,"error_message":"Request parameter error"}

Interrupt 事件
// 流式执行工作流，触发问答节点，Bot提出问题
id: 0
event: Message
data: {"content":"请问你想查看哪个城市、哪一天的天气呢","content_type":"text","node_is_finish":true,"node_seq_id":"0","node_title":"问答"}

id: 1
event: Interrupt
data: {"interrupt_data":{"data":"","event_id":"7404830425073352713/2769808280134765896","type":2},"node_title":"问答"}
查询工作流异步执行结果
工作流异步运行后，查看执行结果。​
接口说明​
调用执行工作流 API 时，如果选择异步执行工作流，响应信息中会返回 execute_id，开发者可以通过本接口查询指定事件的执行结果。​
限制说明​
本 API 的流控限制请参见 API 介绍。​
输出节点的输出数据最多保存 24 小时，结束节点为 7 天。​
输出节点的输出内容超过1MB 时，无法保证返回内容的完整性。​
基础信息​
​
请求方式​
GET
请求地址​
​
https://api.coze.cn/v1/workflows/:workflow_id/run_histories/:execute_id​
权限​
listRunHistory​
确保调用该接口使用的个人令牌开通了 listRunHistory 权限，详细信息参考鉴权方式。​
接口说明​
工作流异步运行后，查看执行结果。​
​
请求参数​
Header​
​
参数​
取值​
说明​
Authorization​
Bearer $Access_Token​
用于验证客户端身份的访问令牌。你可以在扣子平台中生成访问令牌，详细信息，参考准备工作。​
Content-Type​
application/json​
解释请求正文的方式。
​
Path​
​
参数​
类型​
是否必选​
示例​
说明​
workflow_id​
String​
可选​
73505836754923***​
待执行的 Workflow ID，此工作流应已发布。​
进入 Workflow 编排页面，在页面 URL 中，workflow 参数后的数字就是 Workflow ID。例如 https://www.coze.com/work_flow?space_id=42463***&workflow_id=73505836754923***，Workflow ID 为 73505836754923***。​
execute_id​
String​
可选​
743104097880585****​
工作流执行 ID。调用接口执行工作流，如果选择异步执行工作流，响应信息中会返回 execute_id。​
​
返回参数​
​
参数​
类型​
示例​
说明​
code​
Long​
0
调用状态码。0 表示调用成功，其他值表示调用失败，你可以通过 msg 字段判断详细的错误原因。​
msg​
String​
"Success"
状态信息。API 调用失败时可通过此字段查看详细错误信息。​
data​
Array of WorkflowExecuteHistory​
\​
异步工作流的执行结果。​
每次只能查询一个异步事件的执行结果，所以此数组只有一个对象。​
detail​
Object of ResponseDetail​
{"logid":"20241210152726467C48D89D6DB2****"}​
本次请求的执行详情。​
​
WorkflowExecuteHistory​
​
参数​
类型​
示例​
说明​
cost​
String​
0.00000​
预留字段，无需关注。​
execute_id​
Long​
743104097880585****​
执行 ID。​
execute_status​
String​
Success​
执行状态。​
Success：执行成功。​
Running：执行中。​
Fail：执行失败。​
bot_id​
Long​
75049216555930****​
执行工作流时指定的 Agent ID。返回 0 表示未指定智能体 ID。​
connector_id​
Long​
1024​
智能体的发布渠道 ID，默认仅显示 Agent as API 渠道，渠道 ID 为 1024。​
connector_uid​
String​
123​
用户 ID，执行工作流时通过 ext 字段指定的 user_id。如果未指定，则返回 Token 申请人的扣子 ID。​
run_mode​
Integer​
0​
工作流的运行方式：​
0：同步运行。​
1：流式运行。​
2：异步运行。​
output​
String​
{\"Output\":\"{\\\"content_type\\\":1,\\\"data\\\":\\\"来找姐姐有什么事呀\\\",\\\"original_result\\\":null,\\\"type_for_model\\\":2}\"}​
工作流的输出，通常为 JSON 序列化字符串，也有可能是非 JSON 结构的字符串。​
工作流输出的内容包括：​
输出节点的输出。​
结束节点的输出。在扣子代码中，结束节点的输出是通过键（key）Output 来标识。​
工作流输出的结构如下所示：​
​
{​
  "Output": "结束节点的输出内容",​
  "输出节点_1": "输出节点_1的输出内容",​
  "输出节点_2": "输出节点_2的输出内容"​
}​
​
create_time​
Long​
1730174063​
工作流运行开始时间，Unixtime 时间戳格式，单位为秒。​
update_time​
Long​
1730174063​
工作流的恢复运行时间，Unixtime 时间戳格式，单位为秒。​
token​
Long​
​
预留字段，无需关注。​
node_execute_status​
JSON Map​
\​
输出节点的运行情况。字段的格式为：key:node_status,value:map[node_title]*nodeExecuteStatus{}。​
key为节点的名称，如果节点运行了多次，则会随机生成节点名称。​
当输出节点的输出内容超过 1MB 时，调用本 API 会导致返回内容不完整，建议通过查询工作流节点的输出 API 逐一查询各节点的输出内容。​
​
log_id​
String​
20241029152003BC531DC784F1897B***​
工作流异步运行的 Log ID。如果工作流执行异常，可以联系服务团队通过 Log ID 排查问题。​
error_msg​
String​
""​
状态信息。为 API 调用失败时可通过此字段查看详细错误信息。​
error_code​
String​
""​
执行失败调用状态码。0 表示调用成功。其他值表示调用失败。你可以通过 error_message 字段判断详细的错误原因。​
debug_url​
String​
https://www.coze.cn/work_flow?execute_id=743104097880585****&space_id=730976060439760****&workflow_id=742963539464539****​
工作流试运行调试页面。访问此页面可查看每个工作流节点的运行结果、输入输出等信息。​
is_output_trimmed​
Boolean​
​
工作流的输出是否因为过大被清理。true：已清理。false：未清理。​
​
NodeExecuteStatus​
​
参数​
类型​
示例​
说明​
node_id​
String​
node_123​
工作流中的节点 ID。​
is_finish​
Boolean​
true​
工作流中的节点是否已经运行结束。​
loop_index​
Long​
2​
当前节点在循环节点中的循环次数。​
第一次循环时值为 0。​
仅当节点为循环节点，且未嵌套子工作流时，才会返回该参数。​
​
batch_index​
Long​
3​
当前节点在批处理节点中的执行次数。​
第一次执行时值为 0。​
仅当节点为批处理节点，且未嵌套子工作流时，才会返回该参数。​
​
update_time​
Long​
1730174063​
工作流上次运行的时间，采用 Unix 时间戳格式，单位为秒。​
sub_execute_id​
String​
743104097880585****​
子工作流执行的 ID。​
node_execute_uuid​
String​
78923456777*****​
节点每次执行的 ID，用于追踪和识别工作流中特定节点的单次执行情况。​
​
ResponseDetail​
​
参数​
类型​
示例​
说明​
logid​
String​
20241210152726467C48D89D6DB2****​
本次请求的日志 ID。如果遇到异常报错场景，且反复重试仍然报错，可以根据此 logid 及错误码联系扣子团队获取帮助。详细说明可参考获取帮助和技术支持。​
​
示例​
请求示例​
​
curl --location --request curl --location 'https://api.coze.cn/v1/workflows/742963539464539****/run_histories/743104097880585****' \​
--header 'Authorization: Bearer pat_********'​
​
返回示例​
​
{​
    "detail": {​
        "logid": "20241029152003BC531DC784F1897B****"​
    },​
    "code": 0,​
    "msg": "",​
    "data": [​
        {​
            "update_time": 1730174065,​
            "cost": "0.00000",​
            "output": "{\"Output\":\"{\\\"content_type\\\":1,\\\"data\\\":\\\"来找姐姐有什么事呀\\\",\\\"original_result\\\":null,\\\"type_for_model\\\":2}\"}",​
            "bot_id": "742963486232569****",​
            "token": "0",​
            "execute_status": "Success",​
            "connector_uid": "223687073464****",​
            "run_mode": 0,​
            "connector_id": "1024",​
            "logid": "20241029115423ED85C3401395715F726E",​
            "debug_url": "https://www.coze.cn/work_flow?execute_id=743104097880585****&space_id=730976060439760****&workflow_id=742963539464539****",​
            "error_code": "",​
            "error_message": "",​
            "execute_id": "743104097880585****",​
            "create_time": 1730174063​
        }​
    ]​
}​
​

执行工作流
"""
This example describes how to use the workflow interface to chat.
"""

import os
# Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
from cozepy import COZE_CN_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = ''
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = COZE_CN_BASE_URL

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = '{workflow_id}'

# Call the coze.workflows.runs.create method to create a workflow run. The create method
# is a non-streaming chat and will return a WorkflowRunResult class.
workflow = coze.workflows.runs.create(
    workflow_id=workflow_id,
)

print("workflow.data", workflow.data)



执行工作流（流式响应）
"""
This example describes how to use the workflow interface to stream chat.
"""

import os
# Our official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
from cozepy import COZE_CN_BASE_URL

# Get an access_token through personal access token or oauth.
coze_api_token = ''
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = COZE_CN_BASE_URL

from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa

# Init the Coze client through the access_token.
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
workflow_id = '{workflow_id}'


# The stream interface will return an iterator of WorkflowEvent. Developers should iterate
# through this iterator to obtain WorkflowEvent and handle them separately according to
# the type of WorkflowEvent.
def handle_workflow_iterator(stream: Stream[WorkflowEvent]):
    for event in stream:
        if event.event == WorkflowEventType.MESSAGE:
            print("got message", event.message)
        elif event.event == WorkflowEventType.ERROR:
            print("got error", event.error)
        elif event.event == WorkflowEventType.INTERRUPT:
            handle_workflow_iterator(
                coze.workflows.runs.resume(
                    workflow_id=workflow_id,
                    event_id=event.interrupt.interrupt_data.event_id,
                    resume_data="hey",
                    interrupt_type=event.interrupt.interrupt_data.type,
                )
            )


handle_workflow_iterator(
    coze.workflows.runs.stream(
        workflow_id=workflow_id,
    )
)

查询工作流异步执行结果
curl -X GET 'https://api.coze.cn/v1/workflows/{workflow_id}/run_histories/{execute_id}' \
-H "Authorization: Bearer " \
-H "Content-Type: application/json"

