const { evaluate } = require("feelin");
console.log("dyn dur:", evaluate('date("2026-11-25") - duration("P" + string(24) + "M")', {}));
console.log("future ym:", evaluate('years and months duration(date("2027-01-01"), date("2026-11-25"))', {}));
console.log("future ym years:", evaluate('years and months duration(date("2027-01-01"), date("2026-11-25")).years', {}));
console.log("null check:", evaluate('if null = null then -1 else 1', {}));
console.log("empty list count:", evaluate('count([])', {}));
