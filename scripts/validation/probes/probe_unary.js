const { unaryTest } = require("feelin");
const cases = [
  ['not(true)', false],
  ['not(true)', null],
  ['not("MOTORCYCLE", "CAR")', null],
  ['not("MOTORCYCLE", "CAR")', 'TRUCK'],
  ['not("MOTORCYCLE", "CAR")', 'CAR'],
  ['< 17', null],
  ['< 17', -1],
  ['null', null],
  ['null', 0],
  ['null, <= 0', null],
  ['null, <= 0', 0]
];
for (const [e, v] of cases) {
  try {
    console.log(e, '|', JSON.stringify(v), '=>', JSON.stringify(unaryTest(e, { '?': v })));
  } catch (err) {
    console.log(e, '|', JSON.stringify(v), 'ERR:', err.message);
  }
}
