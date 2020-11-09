/**
 * Wrapper around `document.getElementById`
 *
 * @param identifier
 * @returns {HTMLElement}
 */
export function $(identifier){
    return document.getElementById(identifier);
}

/**
 * Make an AJAX GET request and return a Promise
 *
 * @param url
 * @returns {Promise}
 */
export function GET(url) {
    return new Promise(((resolve, reject) => {
        const req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            if (req.readyState === 4 && req.status === 200) {
                const data = JSON.parse(req.responseText);
                resolve(data);
            }
            else if (req.readyState === 4 && req.status >= 400) {
                console.log("Invalid response received");
                console.log(req);
                reject(req);
            }
        }
        req.open("GET", url, true);
        req.send(null);
    }))
}
