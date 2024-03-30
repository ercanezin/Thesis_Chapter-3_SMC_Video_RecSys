"use strict"


addEventListener('load', pickerstart);

//closure are used to set onclick
function pickerstart() {
    var drawCanvas = new Draw();
    drawCanvas.putSeed();
    for (let i = 1; i <= 17; i++) {
        var b = document.getElementById("b" + i.toString());
        b.onclick = mypop(i, b, drawCanvas);
    }

}


function Draw() {
    var seedNum = 150;
    var wwidth = window.innerWidth;
    var wheight = window.innerHeight;
    var canvas = document.getElementById('canvas');
    canvas.width = wwidth;
    canvas.height = wheight;
    var dotSet = [];
    var dotOrig = [];
    var ctx = canvas.getContext('2d');

    canvas.addEventListener('click', function (e) {
        var mousePos = getMousePos(e);
        let timeCome = 0;
        let interval = setInterval(function () {
            timeCome++;
            if (timeCome === 100) {
                clearInterval(interval);
            }
            else if (timeCome < 25) {
                moveDotsToMousePer(mousePos);
            }
            else if (timeCome >= 25) {
                moveDotsToOrig();
            }

        }, 10);
    }, false);

    // move to mouse is limited by the original postion in case all dots assemble together
    function moveDotsToMousePer(mousePos) {
        ctx.clearRect(0, 0, wwidth, wheight);
        var mouseX = mousePos.x, mouseY = mousePos.y;
        for (let i = 0; i < seedNum; i++) {
            var currentDot = dotSet[i];
            moveToMouse(currentDot, mouseX, mouseY);
        }
    }

    function moveDotsToOrig() {
        ctx.clearRect(0, 0, wwidth, wheight);
        for (let i = 0; i < seedNum; i++) {
            var currentDot = dotSet[i];
            var origDot = dotOrig[i];
            if (currentDot.x !== origDot.x || currentDot.y !== origDot.y) {
                currentDot.x = currentDot.x + (origDot.x - currentDot.x) / 20;
                currentDot.y = currentDot.y + (origDot.y - currentDot.y) / 20;
            }
            drawDot(ctx, currentDot);
        }
    }

    function moveToMouse(dot, mouseX, mouseY) {
        dot.x = dot.x + (mouseX - dot.x) / 30;
        dot.y = dot.y + (mouseY - dot.y) / 30;
        drawDot(ctx, dot);
    }

    this.moveToOnePosAndGoBack = function (pos) {
        var timeCome = 0;
        var interval = setInterval(function () {
            timeCome++;
            if (timeCome === 100) {
                clearInterval(interval);
            }
            else if (timeCome < 25) {
                moveDotsToMousePer(pos);
            }
            else if (timeCome >= 25) {
                moveDotsToOrig();
            }
        }, 10);

    }

    this.moveAllDotsTogether = function (pos) {
        var timeCome = 0;
        setInterval(function () {
            timeCome++;
            if (timeCome === 100) {
                clearInterval(interval);
            }
            moveDotsToMousePer(pos)
        }, 10)
    }

    this.putSeed = function () {
        for (let i = 0; i < seedNum; i++) {
            var x = random(wwidth);
            var y = random(wheight);
            var dot = new Dot(x, y, 5);
            var dot_back = new Dot(x, y, 5);
            dotSet.push(dot);
            dotOrig.push(dot_back);
        }
        for (var j = 0; j < seedNum; j++) {

            drawDot(ctx, dotSet[j]);
        }

    }

    function drawDot(ctx, dot) {
        ctx.beginPath();
        ctx.arc(dot.x, dot.y, dot.r, 0, 2 * Math.PI);
        ctx.closePath();
        ctx.fillStyle = "#8A927C";
        ctx.fill();
    }

    function Dot(x, y, r) {
        this.x = x;
        this.y = y;
        this.r = r;
        return this
    }

    function random(limit) {
        return Math.floor((Math.random() * limit) + 1);
    }

    function getMousePos(e) {
        var cRect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - cRect.left,
            y: e.clientY - cRect.top
        };
    }

}


function mypop(index, button, drawCanvas) {
    var pos = {
        x: button.offsetLeft,
        y: button.offsetTop
    };

    var buttonClickNum = 0;

    function popup(event) {
        //move to pose
        drawCanvas.moveToOnePosAndGoBack(pos);

    }

    return popup
}

function changeinput() {
    if (document.getElementById(this.id + 'input').value == 0) {
        document.getElementById(this.id + 'input').value = 1
        this.style.backgroundColor = '#7285a7';

    }
    else {
        document.getElementById(this.id + 'input').value = 0
        this.style.backgroundColor = '#8A927C';

    }
};



