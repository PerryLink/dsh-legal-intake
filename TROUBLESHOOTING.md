# Troubleshooting — dsh-legal-intake

每条按「症状 / 原因 / 动作」写。报错原文都是 `<一句人话>（E_XXX）｜下一步：<动作>`，
把 `E_XXX` 和这句话一起发到 issue 即可定位；不要把真实邮件或客户附件贴进 issue。

## 1. 邮件读不出来（E_LEGAL_EML_INVALID）

- **症状**：`这封邮件缺少 Subject 或 From，读不出是谁发来的什么需求（E_LEGAL_EML_INVALID）｜下一步：补上 Subject 和 From 两个邮件头，或先用自带样例里的 EML`
- **原因**：EML 没有 RFC 5322 头，或 `Subject` / `From` 为空；导出的 `.eml` 被截断也会这样。
- **动作**：用文本编辑器确认前几行有 `Subject:` 和 `From:`；先跑 `node samples/quickstart/run.mjs --check` 确认样例本身是好的。

## 2. 同一封邮件被算了两次（E_LEGAL_MESSAGE_DUPLICATE / E_LEGAL_THREAD_REPEATED）

- **症状**：`这封邮件的 Message-ID 和前面某一封完全相同，会被当成重发（E_LEGAL_MESSAGE_DUPLICATE）｜下一步：确认是不是重发；如果是新需求，请让发件人换一封新邮件`
- **原因**：重发邮件保留了原 `Message-ID`；或者两封不同邮件误用了同一个 `Thread-Id`。
- **动作**：重发就保留现状（入库只算一次）；新需求请让发件人新建邮件。重复 `Thread-Id` 时改成各自的线程号再跑 `legal_intake_doctor`。

## 3. 附件清单对不上（E_LEGAL_ATTACHMENT_DUPLICATE / E_LEGAL_ATTACHMENT_EMPTY）

- **症状**：`同一封邮件里有两个同名附件，导入后只认得出名字（E_LEGAL_ATTACHMENT_DUPLICATE）｜下一步：把重名附件改成不同的文件名，或删掉重复的那一条`
- **原因**：附件清单重复列了同一个文件名，或有一条 `size: 0` 的空附件（常见于没上传成功的扫描件）。
- **动作**：把重名附件改成不同文件名；0 字节附件重新上传或从清单删掉，再重跑 `legal_intake`。

## Install or activation fails

- DSH must satisfy `>=0.2.1-rc.3 <0.4.0`; Node must be `>=24.9 <25`.
- Run `dsh --version` and `node --version`, then retry with a fresh `DSH_HOME`:

```sh
export DSH_HOME="$(mktemp -d)"
dsh plugin --profile <profile> add dsh-legal-intake
dsh --profile <profile> --dump-config | grep dsh-legal-intake
```

## The tool cannot find an input

- All paths are local. Use an absolute path, or a path relative to the process working directory.
- The shipped quickstart lives in `samples/quickstart/`; the repository-only fixtures under `fixtures/` are not in the npm tarball.
- Supported material: EML request files plus an attachment manifest.

## Parse or encoding failures

- Text inputs must be UTF-8; remove a UTF-8 BOM if the first header is reported as unknown.
- Check the EML envelope and that the message has a `Message-ID`; dedupe is by Message-ID / thread.

## Permission or write failures

- Tools marked `R1 local write` write under `$DSH_HOME/storages/dsh-legal-intake`.
- For tests, point `DSH_HOME` at a temporary directory; do not write into a real profile.

## The result looks wrong

- Check the tool boundary in the README first. These are public/synthetic alpha tools, not a production or customer-validated determination.
- Compare the reported row ids and input rows; the output is deliberately explicit about what it could not run.

## Run the tests

```sh
pnpm install --frozen-lockfile
pnpm test
```

## Report

Open an issue on <https://github.com/PerryLink/dsh-legal-intake/issues> with the package version, a minimal synthetic input, and the exact tool call. Do not attach customer data.
