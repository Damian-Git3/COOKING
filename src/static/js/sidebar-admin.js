var button_s = document.querySelectorAll(".Sidebar>ul>a>li");
var ScrollBox_s = document.querySelectorAll(".Sidebar>ul")[0];
var icon = document.querySelectorAll(".Sidebar>ul>a>li>i");
var HoverBox_s = document.getElementsByClassName("HoverBox")[0];
var HoverTip_s = document.getElementsByClassName("HoverTip")[0];

last_item = 0;

function Action_s(Index, Top, Left, side, viewWidth) {
  HoverTip_s.style.animation = "none";
  // Asignar el texto del span dentro del button_s al HoverTip_s
  var spanText = button_s[Index].querySelector("span").textContent;
  HoverTip_s.textContent = spanText;

  HoverBox_s.style.top = Top;
  HoverBox_s.style.left = Left;

  if (Index != last_item) {
    button_s[last_item].classList.remove("Active");
    HoverBox_s.style.animation = "none";
    setTimeout(function () {
      HoverBox_s.style.animation = `Effect 0.25s 1`;
    }, 1);
    button_s[Index].classList.add("Active");
  }

  setTimeout(function () {
    if (side) {
      adjustScrollYPosition(Index);
      setTimeout(function () {
        var altoSpan = HoverTip_s.offsetHeight;
        var iconRect = icon[Index].getBoundingClientRect();
        HoverTip_s.style.animation = `fadeRight 0.25s`;

        var arriba = iconRect.top + (56 - altoSpan) / 2 + "px";
        var izquierda = iconRect.right + 40 + "px";
        // Para pantallas de 768px o más
        HoverTip_s.style.left = izquierda;
        HoverTip_s.style.top = arriba;
      }, 100);
    } else {
      adjustScrollXPosition(Index);

      var anchoSpan = HoverTip_s.offsetWidth;
      var iconRect = icon[Index].getBoundingClientRect();
      HoverTip_s.style.animation = `fadeDown 0.25s`;
      var arriba = iconRect.bottom + 20 + "px";
      var izquierda = viewWidth / 2 - anchoSpan / 2 + "px";
      // Para pantallas de menos de 768px
      HoverTip_s.style.left = izquierda;
      HoverTip_s.style.top = arriba;
    }
  }, 0);

  last_item = Index;
}

function handleMouseover(index) {
  localStorage.setItem("moduloBoton", index);

  var viewWidth = window.innerWidth;

  var actualHeight = button_s[index].offsetTop;
  var actualLength = button_s[index].offsetLeft;

  var side = viewWidth <= 768 ? false : true;

  Action_s(index, `${actualHeight}px`, `${actualLength}px`, side, viewWidth);
}

function returnHoverBoxAfterDelay() {
  var moduloBoton = localStorage.getItem("moduloActivo");
  if (moduloBoton !== null) {
    var index = parseInt(moduloBoton, 10);
    if (!isNaN(index) && index >= 0 && index < button_s.length) {
      handleMouseover(index);
    }
  }
}

function setupMouseoverListeners() {
  hoverTimeoutId = null;
  for (let i = 0; i < button_s.length; i++) {
    icon[i].addEventListener("mouseover", function () {
      handleMouseover(i);
      HoverTip_s.style.display = "block"; // Mostrar HoverTip_s
      setTimeout(function () {
        HoverTip_s.style.opacity = 1;
      } , 250);
      //reiniciar temporizador
      if (hoverTimeoutId !== null) {
        clearTimeout(hoverTimeoutId);
        hoverTimeoutId = null;
      }
    });
    icon[i].addEventListener("mouseout", function () {
      //iniciar temporizador
      hoverTimeoutId = setTimeout(returnHoverBoxAfterDelay, 1000);
      HoverTip_s.style.display = "none";
      HoverTip_s.style.opacity = 0;
    });
    icon[i].addEventListener("click", function () {
      localStorage.setItem("moduloActivo", i);
    });
  }
}

function adjustScrollXPosition(index) {
  ScrollBox_s.style.overflowX = "scroll";
  ScrollBox_s.style.overflowY = "hidden";
  var hoverpositionHorizontal = button_s[index].offsetLeft;

  var buttonWidth = button_s[index].offsetWidth;
  var totalPositionHorizontal = ScrollBox_s.scrollWidth - buttonWidth;
  var relacionHorizontal = hoverpositionHorizontal / totalPositionHorizontal;
  var totalWidth = ScrollBox_s.scrollWidth - ScrollBox_s.clientWidth;
  ScrollBox_s.scrollLeft = relacionHorizontal * totalWidth;
}

function adjustScrollYPosition(index) {
  ScrollBox_s.style.overflowX = "hidden";
  ScrollBox_s.style.overflowY = "scroll";
  var hoverposition = button_s[index].offsetTop;
  var buttonHeight = button_s[index].offsetHeight;
  var alturatotal = ScrollBox_s.scrollHeight - buttonHeight;
  var relacion = hoverposition / alturatotal;
  var totalHeight = ScrollBox_s.scrollHeight - ScrollBox_s.clientHeight;
  ScrollBox_s.scrollTop = relacion * totalHeight;
}

// Ejecutar al cargar la página
document.addEventListener("DOMContentLoaded", function () {
  setupMouseoverListeners();

  // Verificar si existe un valor para moduloBoton en localStorage
  var moduloBoton = localStorage.getItem("moduloBoton");
  if (moduloBoton !== null) {
    // Convertir el valor almacenado a un número y verificar si es un índice válido
    var index = parseInt(moduloBoton, 10);
    if (!isNaN(index) && index >= 0 && index < button_s.length) {
      handleMouseover(index);
    }
  }
});

// Ejecutar cuando se modifique el tamaño de la ventana
window.addEventListener("resize", function () {
  handleMouseover(last_item);
});
