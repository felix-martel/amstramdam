import {$} from "../common/utils";

class Countdown {
    constructor(identifier, duration) {
        this.identifier = identifier;
        this.wrapper = this.el("wrapper");
        this.duration = duration;
        this.interval;
        this.ELEMENTS = ["wrapper", "left", "right"];
    }

    el(which){
        return $(this.identifier + "-" + which)
    }

    showCountdown(){
        this.wrapper.hidden = false;
    }

    hideCountdown(){
        this.wrapper.hidden = true;
    }

    start() {
        clearInterval(this.interval);
        this.showCountdown();
        this.ELEMENTS.forEach(which => {
            this.el(which).setAttribute("data-anim", `base ${which}`);
        });
        this.el("wrapper").style.animationDelay = String(this.duration/2) + "s";
        this.el("left").style.animationDuration = String(this.duration) + "s";
        this.el("right").style.animationDuration = String(this.duration/2) + "s";
        this.interval = setInterval(() => {
            this.end();
        }, this.duration*1000);
    }

    end() {
        this.hideCountdown();
        this.ELEMENTS.forEach(which => {
            this.el(which).setAttribute("data-anim", "");
        })
    }
}
Countdown

export {Countdown as default}