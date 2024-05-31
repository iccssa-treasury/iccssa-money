# 帝国财务

## 报销申请

### 财务类目

**报销:** 个人支付相关活动费用<span style="color:blue;"><b>之后</b></span>由学联返还支出，需要提供**收据**和**付款记录**。

- 收据：商家开具的小票或账单，需清晰显示店名、项目、金额、时间等。
- 付款记录：银行卡或其他渠道的支付记录截图。

**付款:** 以学联名义向第三方<span style="color:blue;"><b>直接支付</b></span>相关活动费用，需要提供**第三方账单**。

**预支:** 在活动费用发生<span style="color:blue;"><b>之前</b></span>从学联获得资金支持，需要事先与财务部进行沟通，事后说明资金使用情况并退还多余款项。

### 外部预算

支出是否<span style="color:blue;"><b>不属于</b></span>本部门预算范围。

开启后，预算方案会显示其他部门的相关预算。

### Business

用于区分个人/企业账户，Monzo等银行转账时会对账户类型进行匹配检查。

### 保存收款账户

开启后，在提交申请时会保存填写的收款账户信息，方便下次使用。

账户信息保存后默认为公开，可在“账户管理”页进行修改（正在开发中）。

### 附件

支持.pdf, .jpg, .jpeg, .png, .doc, .docx, .xls, .xlsx, .ppt, .pptx文件，不超过10MB。

## 更新日志

### 2024-5-31

#### v0.26.331 (beta)

- 添加了**数据导出**功能。
  - 现在可以在后台服务器上以`.csv`格式导出各种财务记录的详细信息。
- 改进了邮件通知系统。
  - 现在的邮件UI与网页更加一致了，内容会显示更多的信息。
  - 现在的邮件会从iccssa.money域名发送，同一主题的邮件可以在邮件客户端中合并显示了。
- 修复了系统周期性崩溃导致无法提交报销申请的bug。

<details>

<summary>历史版本</summary>

<details>

<summary>beta版本</summary>

### 2023-11-27

#### v0.25.452 (beta)

- 添加了**账户管理**页面。
  - 在填写报销申请时保存的收款账户默认为对所有人可见，可在账户管理页面点击👁️图标进行修改。修改后，未公开的账户信息不会出现在报销申请页面的下拉菜单中。
  - 在账户管理页面中点击⭐️图标可以将账户设置为星标。星标账户会在报销申请页面的下拉菜单中置顶显示。
- 在页脚中添加了**更新日志**。

### 2023-11-25

#### v0.24.279 (beta)

- 合并了报销申请页面中的所属部门与预算方案。
  - 删除了报销记录的“所属部门”属性，新的报销记录与其预算方案归属部门一致。
  - 在报销申请页面中添加了“外部预算”选项，开启后，预算方案的下拉菜单中会显示其他部门的预算方案。
- 改进了报销记录页面评论/附件功能的UI。
  - 现在的评论按钮会在上传附件后显示文件样式的图标和“提交”字样。
  - 评论按钮会在评论及附件都为空时隐藏；现在不能发表空的评论了。
- 改进了预算列表页面的UI。
  - 现在的预算列表页面会显示预算方案的状态。
  - 现在的预算列表页面不会显示预算方案的额度了。
- 将网站的图标改为了**帝国学联**的Logo。
- 添加了**首页**的背景图。
- 修复了一些bug。

### 2023-11-16

#### v0.23.283 (beta)

- 添加了**用户文档**。
  - 在报销申请页面添加了一些帮助信息，点击“?”图标可以查看对应选项的详细解释。
- 添加了Markdown模块。
  - 现在可以在评论中使用Markdown语法了。
  - 用户文档和帮助信息也会显示Markdown格式的文本。
- 添加了页脚的**版权信息**，定向至帝国学联官方网站。

### 2023-11-13

#### v0.22.93 (beta)

- 添加了预算方案的状态。
  - 预算方案存在“启用”与“停用”两种状态，新创建的预算方案默认为“启用”状态，所有相关财务活动结束后设置为“停用”状态。
  - 只有“启用”状态的预算方案才会在报销申请页面的下拉菜单中显示。
- 改进了预算列表页面的UI。
  - 现在的预算列表页面会显示预算方案的收入总额。

#### v0.21.1604 (beta)

- 添加了对多文件上传的支持。
- 修复了一些文件上传相关的bug。

### 2023-11-7

#### v0.20.909 (beta)

- 添加了**活动预算**模块。
  - 现在每一笔报销申请都需要选择一个财务部预设的预算方案。
  - 每个部门的执委和部员可以在预算列表中查看自己部门所有活动对应的预算方案。
  - 一些预算方案会有预算额度，可以在活动预算页面中进行查看。
- 修复了一些bug。

### 2023-10-30

#### v0.19.69 (beta)

- 添加了一些测试服务器的配置。

### 2023-10-1

#### v0.18.409 (beta)

- 添加了**通知**模块。
  - 现在可以点击页首的🔔图标查看通知设置，新用户默认为关闭所有通知。
  - 开启通知后，系统会通过邮件发送与用户相关的通知信息。
  - 付款等重要的通知信息会在“仅必要”模式下发送，其他通知信息会在“全部”模式下发送。

### 2023-9-28

#### v0.17.8 (beta)

- 修复了一些bug。

### 2023-9-27

#### v0.16.12 (beta)

- 修复了一些bug。

#### v0.15.287 (beta)

- 添加了报销申请页面对人民币付款方式的支持。
  - 现在支持银行转账、支付宝、微信支付三种报销方式。

#### v0.14.253 (beta)

- 添加了收入记录中对异币种收款的支持。

### 2023-8-9

#### v0.13.179 (beta)

- 改进了报销记录页面历史记录的UI。
  - 现在会显示更简洁的时间信息了。

### 2023-8-8

#### v0.12.974 (beta)

- 添加了**收入记录**模块。
  - 特定用户可以上传学联收入相关的文档并追踪收款状态。
  - 财务部可以在收入记录页面中更新收款状态。

#### v0.11.228 (beta)

- 第一个beta测试版本发布。
- 完善了文件上传功能。

</details>

<details>

<summary>alpha版本</summary>

### 2023-8-6

#### v0.10.137 (alpha)

- 添加了一些服务器配置。

### 2023-8-2

#### v0.9.91 (alpha)

- 添加了文件上传功能。

### 2023-7-2

#### v0.8.659 (alpha)

- 完善了报销记录页面的UI。
  - 添加了历史记录模块。

### 2023-7-1

#### v0.7.1404 (alpha)

- 第一个alpha测试版本发布。
- 添加了前端页面的UI。
- 添加了对单页应用的支持。

</details>

<details>

<summary>pre-alpha版本</summary>

### 2023-6-29

#### v0.6.1350 (pre-alpha)

- 添加了对REST框架及API的支持。

### 2023-6-28

#### v0.5.209 (pre-alpha)

- 添加了一些功能模型的基础结构。

#### v0.4.6835 (pre-alpha)

- 添加了一些前端模型的基础结构。

### 2023-6-27

#### v0.3.110 (pre-alpha)

- 独立了前端和后端的代码库。

### 2023-6-26

#### v0.2.1742 (pre-alpha)

- 添加了一些数据模型的基础结构。

### 2023-6-4

#### v0.1.1043 (pre-alpha)

- 添加了一些开发者工具。
  
</details>

</details>

