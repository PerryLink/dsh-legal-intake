export type IntakeErrorCode = 'E_LEGAL_EML_INVALID' | 'E_LEGAL_DUP_THREAD' | 'E_LEGAL_LEDGER_FAILED'
/** Codes reported in the EML doctor / conflicts output (not thrown). */
export type IntakeIssueCode =
  | 'E_LEGAL_MESSAGE_DUPLICATE'
  | 'E_LEGAL_THREAD_REPEATED'
  | 'E_LEGAL_ATTACHMENT_NAME_EMPTY'
  | 'E_LEGAL_ATTACHMENT_DUPLICATE'
  | 'E_LEGAL_ATTACHMENT_EMPTY'
  | 'E_LEGAL_PARTY_BOTH_SIDES'

/**
 * Human-facing wording for every code this package can surface.
 * Renderer: `<一句人话>（E_CODE）｜下一步：<一个动作>` (Package Standard v1 §4).
 */
const INTAKE_HUMAN: Record<IntakeErrorCode | IntakeIssueCode, { text: string; next: string }> = {
  E_LEGAL_EML_INVALID: {
    text: '这封邮件缺少 Subject 或 From，读不出是谁发来的什么需求',
    next: '补上 Subject 和 From 两个邮件头，或先用自带样例里的 EML',
  },
  E_LEGAL_DUP_THREAD: {
    text: '这封邮件已经在同一个线程里处理过了，没有重复入库',
    next: '如果确实是一封新需求，换一个新的 Thread-Id 再导入',
  },
  E_LEGAL_LEDGER_FAILED: {
    text: '台账没有写出来，刚才的入库结果还在内存里',
    next: '确认导出目录可写，然后重新跑一次 legal.export_ledger',
  },
  E_LEGAL_MESSAGE_DUPLICATE: {
    text: '这封邮件的 Message-ID 和前面某一封完全相同，会被当成重发',
    next: '确认是不是重发；如果是新需求，请让发件人换一封新邮件',
  },
  E_LEGAL_THREAD_REPEATED: {
    text: '两封不同的邮件用了同一个 Thread-Id，线程会被合并',
    next: '检查 Thread-Id；如果不是同一串邮件，请改成各自的线程号',
  },
  E_LEGAL_ATTACHMENT_NAME_EMPTY: {
    text: '附件清单里有一个附件没有文件名',
    next: '补上附件名，或删掉这条空记录再导入',
  },
  E_LEGAL_ATTACHMENT_DUPLICATE: {
    text: '同一封邮件里有两个同名附件，导入后只认得出名字',
    next: '把重名附件改成不同的文件名，或删掉重复的那一条',
  },
  E_LEGAL_ATTACHMENT_EMPTY: {
    text: '附件清单里有一条 0 字节的附件，可能是没上传成功',
    next: '重新上传这个附件，或者从清单里删掉它',
  },
  E_LEGAL_PARTY_BOTH_SIDES: {
    text: '同一个当事人在新事项里同时是委托方和对方',
    next: '先确认当事人角色，只保留一边再跑冲突预检',
  },
}

export function intakeErrorMessage(code: IntakeErrorCode | IntakeIssueCode | string): string {
  const human = INTAKE_HUMAN[code as IntakeErrorCode | IntakeIssueCode]
  if (!human) return `处理这封邮件时出错了（${code}）｜下一步：把 EML 和这条错误一起发到 issue`
  return `${human.text}（${code}）｜下一步：${human.next}`
}

export class IntakeError extends Error {
  readonly code: IntakeErrorCode
  /** Technical detail for logs; never shown as the user-facing sentence. */
  readonly detail: string
  constructor(code: IntakeErrorCode, detail = '') {
    super(intakeErrorMessage(code))
    this.name = 'IntakeError'
    this.code = code
    this.detail = detail
  }
}
export interface Eml { message_id: string; thread_id: string; subject: string; from: string; date: string; body: string; attachments: { name: string; sha256: string; size: number }[] }
export function parseEml(text: string, attachments: Eml['attachments'] = []): Eml {
  const split = text.split(/\r?\n\r?\n/)
  const head = split.shift() ?? ''
  const body = split.join('\n\n').trim()
  const h = (name: string) => { const m = new RegExp(`^${name}:\\s*(.+)$`, 'im').exec(head); return m?.[1]?.trim() ?? '' }
  const subject = h('Subject'), from = h('From'), date = h('Date'), mid = h('Message-ID') || `mid-${hash(text)}`
  const thread = h('Thread-Id') || mid
  if (!subject || !from) throw new IntakeError('E_LEGAL_EML_INVALID', 'EML needs Subject and From')
  return { message_id: mid, thread_id: thread, subject, from, date, body, attachments }
}
export function hash(text: string): string { let h = 5381; for (let i = 0; i < text.length; i++) h = ((h << 5) + h + text.charCodeAt(i)) | 0; return Math.abs(h).toString(36) }
export function classify(subject: string, body: string): string { const t = `${subject}\n${body}`; if (/NDA|保密协议/i.test(t)) return 'NDA'; if (/MSA|主协议|框架协议/i.test(t)) return 'MSA'; if (/审查|审阅|review/i.test(t)) return 'CONTRACT_REVIEW'; if (/诉讼|仲裁|争议/i.test(t)) return 'DISPUTE'; if (/合规|GDPR|数据/i.test(t)) return 'COMPLIANCE'; return 'OTHER' }
