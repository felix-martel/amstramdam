/**
 * Add whitespace every 3 digits, and convert to French notation
 * (that is, "," instead of "." for floating point numbers)
 *
 * @param n
 * @returns {string}
 */
export function numberFormatter(n) {
    return String(n)
        .replace(/(?!^)(?=(?:\d{3})+(?:\.|$))/gm, ' ')
        .replace(".", ",")
}

/**
 * Format a distance depending on the scale (useMeters = true/false)
 * @param d
 * @param useMeters
 * @returns {{unit: string, distance: number | string, toString: (function(): string), float: boolean}}
 */
export function formatDistance(d, useMeters = true){
    let distance, unit;
    if (d === "-") {
        distance = "-";
        unit = "";
    } else if (useMeters){
        if (d >= 2) {
            distance = Math.round(d*100) / 100;
            unit = "km";
        } else {
            distance = Math.round(d * 1000);
            unit = "m";
        }
    } else {
        distance = Math.round(d);
        unit = "km";
    }
    return {
        distance,
        unit,
        float: (useMeters && unit==="km"),
        toString: () => `${numberFormatter(distance)} ${unit}`
    }
}