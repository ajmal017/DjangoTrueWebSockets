document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket("ws://127.0.0.1:8080/ws");

    socket.onopen = function () {
        console.log("Connection established");
    };

    socket.onclose = function (event) {
        if (event.wasClean) {
            console.log('Connection closed');
        } else {
            console.log('Connection closed(bad)'); // например, "убит" процесс сервера
        }
        console.log('Code: ' + event.code + ' Reason: ' + event.reason);
    };

    socket.onmessage = function (event) {
        console.log("Took", Date.now() - beg);
        console.log("Data: " + event.data);
        l.add(event.data);
    };

    socket.onerror = function (error) {
        console.log("Error: " + error.message);
    };

    let beg = Date.now();
    button = document.querySelector('#posts');
    button.addEventListener('click', () => {
        beg = Date.now();
        socket.send('posts');
    })

    const l = new PopupList();
    // l.add("Why not? 1");
    // setTimeout(() => {
    //     l.add("Why not? 2");
    // }, 1000);
    // let k = 0;
    // setInterval(() => {
    //     l.add(`why not? ${++k}`);
    // }, 100);
})

class Popup {
    constructor(text) {
        this.text = text;

        const domElement = document.createElement('div');
        domElement.classList.add('pop-up', 'toggle');
        domElement.innerText = text;
        this.domElement = domElement;
    }

    show() {
        this.domElement.classList.remove('toggle');
    }
    hide() {
        this.domElement.classList.add('toggle');
    }
}

const timeOut = 2000;

class PopupList {
    constructor() {
        this.container = document.querySelector('.pop-ups');
        this.elements = [];
    }
    add(text) {
        const newElement = new Popup(text);
        this.elements.push(newElement);
        setTimeout(() => this._remove(newElement), timeOut);

        this.container.appendChild(newElement.domElement);
        console.log(newElement.domElement.classList);

        setTimeout(() => {
            newElement.show();
        }, 0);
    }
    /**
     * 
     * @param {Popup} element 
     */
    _remove(element) {
        // const index = this.elements.indexOf(element);
        this.elements = this.elements.filter(el => el != element);

        setTimeout(() => {
            element.hide();
        }, 0);
        // element.hide();
        setTimeout(() => {
            this.container.removeChild(element.domElement);
        }, 2000);
    }

}