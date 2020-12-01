import {$} from "../common/utils";


class ChatBox {
    constructor({input, messageList,
        wrapper,
        toggleButton,
        closeButton,
        onSend, onReceive} = {}) {
        this.input = $(input)
        this.messageList = $(messageList)
        this.wrapper = $(wrapper)
        this.toggleButton = $(toggleButton)
        this.closeButton = $(closeButton)
        this.socket = socket
        this.hooks = {
            onSend: [],
            onReceive: []
        }
        if (typeof onSend !== "undefined"){
            this.hooks.onSend.add(onSend)
        }
        if (typeof onReceive !== "undefined"){
            this.hooks.onReceive.add(onReceive)
        }

        this.initEvents()
    }

    onSend(func) {
        this.hooks.onSend.add(func)
    }

    onReceive(func) {
        this.hooks.onReceive.add(func)
    }

    initEvents() {
        this.input.addEventListener("keyup", e => {
            if (e.keyCode === 13){
                const message = this.input.value;
                this.hooks.forEach(f => {
                    f(message);
                })
                this.input.value = "";
            }
        })
        // TODO: implement toggle/close/cookie storage/unread messages
    }

    appendMessage(message, author) {
        const el = `<div class="chat-message"><span class="chat-author">${author}</span><span class="chat-message-content">${message}</span></div>`;
        this.messageList.inner += el;
    }
}

class ChatManager {
    constructor(chatboxes) {
        this.boxes = chatboxes.map(opt => new ChatBox(opt))
    }

    appendMessage(message, author) {
        const el = `<div class="chat-message"><span class="chat-author">${getPlayerName(author)}</span><span class="chat-message-content">${message}</span></div>`;
        this.messages.forEach(messages => {
            messages.inner += el;
        });
    }


}