var button_s = document.querySelectorAll(".Sidebar>ul>a>li");
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
  HoverBox_s.style.opacity = 1;

  if (Index != last_item) {
    button_s[last_item].classList.remove("Active");
    HoverBox_s.style.animation = "none";
    setTimeout(function () {
      HoverBox_s.style.animation = `Effect 0.25s 1`;
    }, 1);
    button_s[Index].classList.add("Active");
  }

  setTimeout(function () {
    var iconRect = icon[Index].getBoundingClientRect();
    var anchoSpan = HoverTip_s.offsetWidth;
    var altoSpan = HoverTip_s.offsetHeight;

    HoverTip_s.style.opacity = 1;

    if (side) {
      HoverTip_s.style.animation = `fadeRight 0.25s`;

      var arriba = iconRect.top + (56 - altoSpan) / 2 + "px";
      var izquierda = iconRect.right + 40 + "px";
      // Para pantallas de 768px o más
      HoverTip_s.style.left = izquierda;
      HoverTip_s.style.top = arriba;
    } else {
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

function setupMouseoverListeners() {
  for (let i = 0; i < button_s.length; i++) {
    icon[i].addEventListener("mouseover", function () {
      handleMouseover(i);
      HoverTip_s.style.display = "block"; // Mostrar HoverTip_s
    });
    icon[i].addEventListener("mouseout", function () {
      HoverTip_s.style.display = "none";
      HoverTip_s.style.opacity = "0";
    });
  }
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
