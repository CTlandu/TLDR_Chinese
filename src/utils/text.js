// 剥掉标题开头的 emoji 序列（含变体选择符、ZWJ）及其后空格。
// 只匹配开头，正常中文/英文/数字开头的标题不受影响。
// U+229E(⊞) 和 U+20BF(₿) 不是标准 emoji，但后端旧逻辑会用它们当 Microsoft/Bitcoin 图标，一并剥掉。
export function stripLeadingEmoji(str) {
  if (!str) return str;
  return str.replace(
    /^[\p{Extended_Pictographic}\p{Emoji_Presentation}⊞₿️‍\s]+/u,
    ''
  );
}

// 去掉英文标题结尾的阅读时长标注，如 "(5 minute read)"。
export function stripReadingTime(str) {
  if (!str) return str;
  return str.replace(/\s*\(\d+\s*minute read\)\s*$/i, '').trim();
}
