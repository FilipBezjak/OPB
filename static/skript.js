    /*use strict, da ni globalna spremenljivka al nekaj 
    podpicja opcijska, ... nam da vse vrednosti iterabilnega objekta*/
    'use strict'

    function isci() {
      let vrednost = document.getElementById('isci').value;
      let vrednostC = vrednost.toLocaleLowerCase();
      let tabela = document.getElementById('izpis');
      let vrstice = tabela.rows;
    for (let i = 0; i < vrstice.length; i++) {
      let igralec = vrstice[i].cells[0].innerText;
      if (igralec.toLocaleLowerCase().indexOf(vrednostC) > -1) {
        vrstice[i].style.display = "";
      } else {
        vrstice[i].style.display = "none";
        /*more bit vsaj enkrat none, da ga ne pokaže*/
      }
    }}



    /* da se pokažejo izbire ko kliknemo */
function izbire_gumb() {
    document.getElementById("izbireGumb").classList.toggle("show");
  }

  function isci2() {
    let input = document.getElementById("vnos");
    let filter = input.value.toUpperCase();
    let div = document.getElementById("izbireGumb");
    let a = div.getElementsByTagName("a");
    /*a je seznam igralcev*/
    /*pogleda, če so vse črke iz inputa v besedi. To je dosti hitreje, kot če bi gledali če je input kot celota v besedi */
    for (let i = 0; i < a.length; i++) {
      let txtValue = a[i].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
      } else {
        a[i].style.display = "none";
        /*more bit vsaj enkrat none, da ga ne pokaže*/
      }
    }
  }

  function redirect_ekipe() {
    let currentURL = window.location.href;
    let poskodbe = currentURL.charAt(currentURL.length - 1);
    if (poskodbe="f") {
        redirectTo = currentURL.replace("http://localhost:8080/igralci/ff", "http://localhost:8080/igralci/tf");
        window.location.href = redirectTo;
    }
    else {
        redirectTo = currentURL.replace("http://localhost:8080/igralci/ft", "http://localhost:8080/igralci/tt");
        window.location.href = redirectTo;
    }
}    
function redirect_poskodbe() {
    let currentURL = window.location.href;
    let ekipe = currentURL.charAt(currentURL.length - 2);
    if (ekipe="f") {
        let redirectTo = currentURL.replace("http://localhost:8080/igralci/ff", "http://localhost:8080/igralci/ft");
        window.location.href = redirectTo;
    }
    else {
        let redirectTo = currentURL.replace("http://localhost:8080/igralci/tf", "http://localhost:8080/igralci/tt");
        window.location.href = redirectTo;
    }
} 