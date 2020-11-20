
export class CookieHandler {
    constructor (name) {
        this.name = encodeURIComponent(name);
        this.pattern = new RegExp("(?:(?:^|.*;\\s*)" + this.name + "\\s*\\=\\s*([^;]*).*$)|^.*$");
        // this.defaultValue = defaultValue;
    }

    encode(value) {
        return encodeURIComponent(value);
    }

    decode(value){
        return decodeURIComponent(value);
    }

    write(value, neverExpire = false){
        const expires = neverExpire ? ";max-age=31536000" : "";
        document.cookie = this.name + "=" + this.encode(value) + expires;
    }

    read() {
        let value = document.cookie
          .split('; ')
          .find(row => row.startsWith(this.name+"="))
        if (typeof value === "undefined") {
            return undefined;
        }
        value = value.split('=')[1];
        return this.decode(value);
    }

    remove(){
        // TODO
        document.cookie = this.name + "=;expires=Thu, 01 Jan 1970 00:00:01 GMT";
    }

    exists() {
        return document.cookie.split('; ').some(row => row.startsWith(this.name+"="));
    }
}

export class BooleanCookieHandler extends CookieHandler {
    encode (value) {
        return value ? "1" : "0";
    }
    decode (value){
        return value === "1";
    }

    storeTrue(){
        this.write(true);
    }

    storeFalse(){
        this.write(false);
    }
}

export class IntCookieHandler {
    decode (value) {
        return parseInt(value)
    }
}

export class BooleanSettingHandler {
    constructor(settingName, store) {
        this.name = settingName;
        this.handler = new BooleanCookieHandler("ams_" + this.name);
        this.store = store;
        if (this.handler.exists()){
            this.state = this.handler.read();
        }
    }

    get state() {
        return this.store.state.playerParams[this.name];
    }

    set state(value) {
        this.handler.write(value);
        this.store.commit("updateParams", {key: this.name, value: value});
    }
}