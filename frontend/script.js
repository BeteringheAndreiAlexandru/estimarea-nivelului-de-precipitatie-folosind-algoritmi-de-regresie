// 1. Funcția pentru Modul Manual (Când utilizatorul apasă Calculează)
document.getElementById('predictBtn').addEventListener('click', async () => {
    const month = parseInt(document.getElementById('month').value);
    const tmin = parseFloat(document.getElementById('tmin').value);
    const tmax = parseFloat(document.getElementById('tmax').value);
    
    const tavg = (tmin + tmax) / 2;

    const payload = {
        month: month,
        tavg: tavg,
        tmin: tmin,
        tmax: tmax
    };

    try {
        const response = await fetch('http://127.0.0.1:8001/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            const resultCard = document.getElementById('resultCard');
            const resultValue = document.getElementById('resultValue');
            const weatherIcon = document.getElementById('weatherIcon');

            resultCard.style.display = 'block';
            
            const mm = data.estimated_precipitation_mm;
            resultValue.innerText = `${mm} mm`;

            if (mm === 0) weatherIcon.innerText = "☀️ Nu sunt șanse de ploaie.";
            else if (mm < 5) weatherIcon.innerText = "🌦️ Posibil ploaie ușoară.";
            else weatherIcon.innerText = "🌧️ Ploaie serioasă înregistrată.";

        } else {
            alert('Eroare de la server. Verifică terminalul Python!');
        }
    } catch (error) {
        alert('Nu mă pot conecta la Backend. Asigură-te că rulează pe portul 8001.');
        console.error(error);
    }
});

// 2. Funcția pentru Prognoza Live pe 7 Zile (Când se apasă butonul verde)
document.getElementById('liveForecastBtn').addEventListener('click', async () => {
    const container = document.getElementById('forecastContainer');
    container.innerHTML = "<p style='text-align:center;'>Se preiau datele de pe satelit și se rulează AI-ul...</p>";

    try {
        // Cerem datele de la ruta nouă
        const response = await fetch('http://127.0.0.1:8001/forecast-7-days');
        const data = await response.json();

        if (data.prognoza) {
            container.innerHTML = ""; // Curățăm mesajul de așteptare
            
            data.prognoza.forEach(zi => {
                let icon = "☀️";
                if (zi.ploaie_estimata_mm > 0 && zi.ploaie_estimata_mm < 5) icon = "🌦️";
                else if (zi.ploaie_estimata_mm >= 5) icon = "🌧️";

                // Creăm o "carte" de vizită pentru fiecare zi
                const ziDiv = document.createElement('div');
                ziDiv.style.background = "#fff";
                ziDiv.style.padding = "15px";
                ziDiv.style.borderRadius = "8px";
                ziDiv.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
                ziDiv.style.display = "flex";
                ziDiv.style.justifyContent = "space-between";
                ziDiv.style.alignItems = "center";
                
                ziDiv.innerHTML = `
                    <div>
                        <strong>${zi.data}</strong><br>
                        <span style="color: #666; font-size: 0.9em;">Min: ${zi.tmin}°C | Max: ${zi.tmax}°C</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.5em;">${icon}</span><br>
                        <strong>${zi.ploaie_estimata_mm} mm</strong>
                    </div>
                `;
                container.appendChild(ziDiv);
            });
        } else if (data.error) {
            container.innerHTML = `<p style="color: red;">Eroare: ${data.error}</p>`;
        }
    } catch (error) {
        alert("Eroare la conectarea cu serverul! Asigură-te că Python rulează pe portul 8001.");
        container.innerHTML = "";
    }
});