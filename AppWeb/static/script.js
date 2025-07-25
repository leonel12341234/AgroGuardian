function handleLogin(event) {
    event.preventDefault();
    // Simula validación o procesamiento
    alert("Inicio de sesión exitoso");
    window.location.href = "dashboard.html"; // Cambiá por la página que quieras
  }

  function handleRegister(event) {
    event.preventDefault();
    const password = document.getElementById("registerPassword").value;
    const confirm = document.getElementById("registerConfirmPassword").value;

    if (password !== confirm) {
      alert("Las contraseñas no coinciden.");
      return;
    }

    alert("Registro exitoso");
    window.location.href = "dashboard.html"; // Cambiá por la página que quieras
  }
     
      const secciones = [
        "login",
        "register",
        "caracteristicas",
        "beneficios",
        "contacto",
      ];

      function mostrarSolo(id) {
        secciones.forEach((seccionId) => {
          document.getElementById(seccionId).style.display =
            seccionId === id ? "block" : "none";
        });
      }

      document
        .getElementById("loginLink")
        .addEventListener("click", () => mostrarSolo("login"));
      document
        .getElementById("registerLink")
        .addEventListener("click", () => mostrarSolo("register"));
      document
        .getElementById("carac")
        .addEventListener("click", () => mostrarSolo("caracteristicas"));
      document
        .getElementById("benef")
        .addEventListener("click", () => mostrarSolo("beneficios"));
      document
        .getElementById("contactLink")
        .addEventListener("click", () => mostrarSolo("contacto"));