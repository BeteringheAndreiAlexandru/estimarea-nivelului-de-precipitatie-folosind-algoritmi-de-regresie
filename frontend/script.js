let graficActiv = null;
let aiGraficActiv = null;
let datePrognozaCurenta = null;

// Funcția 1: Modul Manual
document.getElementById('predictBtn').addEventListener('click', async () => {
    const month = parseInt(document.getElementById('month').value);
    const tmin = parseFloat(document.getElementById('tmin').value);
    const tmax = parseFloat(document.getElementById('tmax').value);
    const humidity = parseFloat(document.getElementById('humidity').value);
    const pressure = parseFloat(document.getElementById('pressure').value);
    const tavg = (tmin + tmax) / 2;

    const payload = { month, tavg, tmin, tmax, humidity, pressure };

    try {
        const response = await fetch('http://127.0.0.1:8001/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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

            if (mm === 0) weatherIcon.innerText = "☀️ Însorit / Senin";
            else if (mm > 0 && mm < 1) weatherIcon.innerText = "⛅ Parțial înnorat / Burniță";
            else if (mm >= 1 && mm < 5) weatherIcon.innerText = "🌦️ Ploaie ușoară";
            else weatherIcon.innerText = "🌧️ Ploaie moderată / Torențială";
        } else {
            alert('Eroare de la server. Verifică terminalul Python!');
        }
    } catch (error) {
        alert('Nu mă pot conecta la Backend. Asigură-te că rulează pe portul 8001.');
    }
});

// Funcția 2: Prognoza Live pe 7 Zile (Aici este inclus spinner-ul)
document.getElementById('liveForecastBtn').addEventListener('click', async () => {
    const container = document.getElementById('forecastContainer');
    const exportBtn = document.getElementById('exportBtn');
    const spinner = document.getElementById('loadingSpinner'); 
    const orasSelectat = document.getElementById('orasSelect').value;
    
    
    container.innerHTML = ""; 
    exportBtn.style.display = 'none'; 
    spinner.style.display = 'flex'; 

    try {
        const response = await fetch(`http://127.0.0.1:8001/forecast-7-days?oras=${orasSelectat}`);
        const data = await response.json();

        // Oprim spinner-ul imediat ce vin datele
        spinner.style.display = 'none';

        if (data.prognoza) {
            datePrognozaCurenta = data.prognoza; 
            exportBtn.style.display = 'block';   
            
            data.prognoza.forEach(zi => {
                let icon = "☀️";
                let textVreme = "Însorit";

                if (zi.ploaie_estimata_mm === 0) {
                    icon = "☀️"; textVreme = "Senin";
                } else if (zi.ploaie_estimata_mm > 0 && zi.ploaie_estimata_mm < 1) {
                    icon = "⛅"; textVreme = "Parțial înnorat";
                } else if (zi.ploaie_estimata_mm >= 1 && zi.ploaie_estimata_mm < 5) {
                    icon = "🌦️"; textVreme = "Ploaie ușoară";
                } else if (zi.ploaie_estimata_mm >= 5 && zi.ploaie_estimata_mm < 15) {
                    icon = "🌧️"; textVreme = "Ploaie moderată";
                } else {
                    icon = "⛈️"; textVreme = "Furtună";
                }

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
                        <span style="color: #666; font-size: 0.9em;">Min: ${zi.tmin}°C | Max: ${zi.tmax}°C</span><br>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.5em;">${icon}</span><br>
                        <strong>${zi.ploaie_estimata_mm} mm</strong><br>
                        <span style="color: #3498db; font-size: 0.85em; font-weight: bold;">${textVreme}</span>
                    </div>
                `;

                const btnGrafic = document.createElement('button');
                btnGrafic.className = 'btn-grafic';
                btnGrafic.innerText = "🌡️ Grafic Temperaturi";
                btnGrafic.onclick = () => deseneazaGrafic(zi.data, zi.grafic_ore, zi.grafic_temperaturi, orasSelectat);
                
                ziDiv.children[0].appendChild(btnGrafic);
                container.appendChild(ziDiv);
            });
        } else if (data.error) {
            container.innerHTML = `<p style="color: red;">Eroare: ${data.error}</p>`;
        }
    } catch (error) {
        // În caz de eroare (ex: server oprit), ascundem spinner-ul
        spinner.style.display = 'none';
        alert("Eroare la conectarea cu serverul!");
        container.innerHTML = "";
    }
});

// Funcția de Export CSV
document.getElementById('exportBtn').addEventListener('click', () => {
    if (!datePrognozaCurenta) return;

    const orasSelectat = document.getElementById('orasSelect').value;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Data,Temperatura Minima (C),Temperatura Maxima (C),Precipitatii Estimate AI (mm)\n";

    datePrognozaCurenta.forEach(zi => {
        csvContent += `${zi.data},${zi.tmin},${zi.tmax},${zi.ploaie_estimata_mm}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `prognoza_ai_${orasSelectat.toLowerCase().replace('-', '_')}.csv`);
    document.body.appendChild(link); 
    
    link.click(); 
    document.body.removeChild(link); 
});

// Funcția 3: Transparența Modelului (XAI)
document.getElementById('explainAIBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('http://127.0.0.1:8001/feature-importance');
        const data = await response.json();
        
        document.getElementById('aiModal').style.display = 'flex';
        const ctx = document.getElementById('aiChart').getContext('2d');
        
        if (aiGraficActiv) aiGraficActiv.destroy();

        const labels = Object.keys(data).map(key => {
            if (key === 'month') return 'Luna Anului';
            if (key === 'tavg') return 'Temp. Medie';
            if (key === 'tmin') return 'Temp. Minimă';
            if (key === 'tmax') return 'Temp. Maximă';
            if (key === 'humidity') return 'Umiditate (%)';
            if (key === 'pressure') return 'Presiune Atmosferică';
            return key;
        });
        const values = Object.values(data);

        aiGraficActiv = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['#3498db', '#9b59b6', '#e74c3c', '#f1c40f', '#2ecc71', '#34495e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right' } }
            }
        });
    } catch (error) {
        alert("Eroare la conectarea cu serverul pentru a afla decizia AI!");
    }
});

function deseneazaGrafic(dataZi, ore, temperaturi, oras) {
    document.getElementById('chartModal').style.display = 'flex';
    document.getElementById('chartTitle').innerText = `Temperaturi pe ore în ${oras} (${dataZi})`;
    const ctx = document.getElementById('tempChart').getContext('2d');
    if (graficActiv) graficActiv.destroy();
    graficActiv = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ore,
            datasets: [{
                label: `Temperatura (°C)`,
                data: temperaturi,
                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                borderColor: 'rgba(192, 57, 43, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { title: { display: true, text: 'Grade Celsius (°C)' } },
                x: { title: { display: true, text: 'Ora' } }
            }
        }
    });
}

function inchideModal() { document.getElementById('chartModal').style.display = 'none'; }
function inchideAIModal() { document.getElementById('aiModal').style.display = 'none'; }