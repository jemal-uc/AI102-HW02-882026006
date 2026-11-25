const { evaluate } = require("feelin");
console.log("parens true:", evaluate('(vehicleType in ["MOTORCYCLE", "CAR"]) and (performanceClass in ["SPORT", "HIGH_PERFORMANCE"])', { vehicleType: "MOTORCYCLE", performanceClass: "SPORT" }));
console.log("parens false:", evaluate('(vehicleType in ["MOTORCYCLE", "CAR"]) and (performanceClass in ["SPORT", "HIGH_PERFORMANCE"])', { vehicleType: "TRUCK", performanceClass: "HIGH_PERFORMANCE" }));
console.log("list contains:", evaluate('list contains(["MOTORCYCLE", "CAR"], vehicleType) and list contains(["SPORT", "HIGH_PERFORMANCE"], performanceClass)', { vehicleType: "TRUCK", performanceClass: "HIGH_PERFORMANCE" }));
console.log("decimal:", evaluate('decimal(200000000 * 0.018, 0)', {}));
console.log("round half up:", evaluate('round half up(200000000 * 0.018, 0)', {}));
console.log("decimal D09:", evaluate('decimal(decimal(200000000 * 0.018, 0) * (1 + 0.0), 0)', {}));
