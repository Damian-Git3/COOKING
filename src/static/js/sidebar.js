var button_s = document.querySelectorAll(".MenuBox>ul>li");
var svg_s = document.querySelectorAll(".MenuBox>ul>li>svg");
var HoverBox_s = document.getElementsByClassName("HoverBox")[0];

function clearTag(id) {
    for (let item of svg_s) {
        if (item == svg_s[id]) {
            continue;
        }
        item.style.color = "#6e6c6c";
    }
}

function Action_s(Index, Top) {
    HoverBox_s.style.top = Top;
    HoverBox_s.style.animation = `Effect_${Index} 250ms 1`;
    svg_s[Index].style.color = "white"
    clearTag(Index)
}
button_s[0].addEventListener("mouseover", function() {
    Action_s(0, "20px");
});

button_s[1].addEventListener("mouseover", function() {
    Action_s(1, "87px");
});

button_s[2].addEventListener("mouseover", function() {
    Action_s(2, "154px");
});

button_s[3].addEventListener("mouseover", function() {
    Action_s(3, "221px");
});

button_s[4].addEventListener("mouseover", function() {
    Action_s(4, "288px");
});

button_s[5].addEventListener("mouseover", function() {
    Action_s(5, "355px");

});