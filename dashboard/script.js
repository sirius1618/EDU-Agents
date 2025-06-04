let comparisonChart, absencesChart, participationChart, correlationChart, topStudentsChart;

async function loadDashboardData() {
    try {
        document.querySelectorAll('.stat-card p').forEach(p => {
            p.textContent = 'Carregando...';
        });

        const response = await fetch('http://localhost:5000/dashboard/api');

        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status}`);
        }

        const data = await response.json();

        document.getElementById('math-avg').textContent = data.stats.math_avg.toFixed(2);
        document.getElementById('language-avg').textContent = data.stats.language_avg.toFixed(2);
        document.getElementById('high-absences').textContent = data.stats.high_absences;
        document.getElementById('low-homework').textContent = data.stats.low_homework;

        renderComparisonChart(data.comparison);
        renderAbsencesChart(data.scatter_absences);
        renderParticipationChart(data.scatter_participation);
        renderCorrelationChart(data.correlation);
        renderTopStudentsChart(data.top_students);

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        document.querySelectorAll('.stat-card p').forEach(p => {
            p.textContent = 'Erro';
            p.style.color = '#e74c3c';
        });
    }
}

function renderComparisonChart(data) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');

    if (comparisonChart) comparisonChart.destroy();

    comparisonChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Matemática',
                    data: data.math.map((value, index) => ({x: index + 1, y: value})),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    pointRadius: 5
                },
                {
                    label: 'Linguagens',
                    data: data.language.map((value, index) => ({x: index + 1, y: value})),
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    pointRadius: 5
                },
                {
                    label: 'Desempenho Anterior',
                    data: data.previous.map((value, index) => ({x: index + 1, y: value})),
                    backgroundColor: 'rgba(255, 159, 64, 0.7)',
                    pointRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Notas'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Alunos'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`;
                        }
                    }
                }
            }
        }
    });
}

function renderAbsencesChart(data) {
    const ctx = document.getElementById('absencesChart').getContext('2d');

    if (absencesChart) absencesChart.destroy();

    absencesChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Faltas vs Notas Matemática',
                data: data,
                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Nota em Matemática'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Número de Faltas'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Nota: ${context.parsed.y.toFixed(1)} | Faltas: ${context.parsed.x}`;
                        }
                    }
                }
            }
        }
    });
}

function renderParticipationChart(data) {
    const ctx = document.getElementById('participationChart').getContext('2d');

    if (participationChart) participationChart.destroy();

    participationChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Participação vs Notas Matemática',
                data: data,
                backgroundColor: 'rgba(46, 204, 113, 0.7)',
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Nota em Matemática'
                    }
                },
                x: {
                    min: 0.3,
                    max: 1.0,
                    title: {
                        display: true,
                        text: 'Nível de Participação'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Nota: ${context.parsed.y.toFixed(1)} | Participação: ${context.parsed.x.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

function renderCorrelationChart(data) {
    const ctx = document.getElementById('correlationChart').getContext('2d');

    if (correlationChart) correlationChart.destroy();

    const labels = Object.keys(data).filter(key => key !== 'student_id');
    const datasets = [];

    labels.forEach((label, i) => {
        datasets.push({
            label: label,
            data: labels.map(l => data[label][l]),
            backgroundColor: `hsl(${i * 60}, 70%, 70%)`,
            borderColor: `hsl(${i * 60}, 70%, 50%)`,
            borderWidth: 1
        });
    });

    correlationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: -1,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Correlação'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label} ↔ ${context.label}: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });
}

function renderTopStudentsChart(data) {
    const ctx = document.getElementById('topStudentsChart').getContext('2d');

    if (topStudentsChart) topStudentsChart.destroy();

    const labels = data.map(item => `Aluno ${item.student_id}`);
    const scores = data.map(item => item.math_score);

    topStudentsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nota em Matemática',
                data: scores,
                backgroundColor: 'rgba(52, 152, 219, 0.7)',
                borderColor: 'rgba(41, 128, 185, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Nota'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Nota: ${context.parsed.x.toFixed(1)}`;
                        }
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setInterval(loadDashboardData, 30000);  // Atualizar a cada 30 segundos
});

function renderStudentComparisonChart(data) {
    const ctx = document.getElementById('studentComparisonChart').getContext('2d');

    if (window.studentComparisonChart && typeof window.studentComparisonChart.destroy === 'function') {
        window.studentComparisonChart.destroy();
    }

    window.studentComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Matemática', 'Linguagens', 'Participação', 'Tarefas', 'Desempenho Anterior'],
            datasets: [
                {
                    label: 'Aluno',
                    data: [
                        data.student_info.math_score,
                        data.student_info.language_score,
                        data.student_info.participation,
                        data.student_info.homework_completion,
                        data.student_info.previous_performance
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                },
                {
                    label: 'Média da Turma',
                    data: [
                        data.class_avg.math_score,
                        data.class_avg.language_score,
                        data.class_avg.participation,
                        data.class_avg.homework_completion,
                        data.class_avg.previous_performance
                    ],
                    backgroundColor: 'rgba(255, 206, 86, 0.7)'
                }
            ]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}



// Função para carregar dados do aluno, sem parâmetro (pega do input)
async function loadStudentDashboardData() {
    const studentId = document.getElementById('studentIdInput').value;
    if (!studentId) {
        alert('Por favor, insira um ID de aluno.');
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/dashboard/api/student/${studentId}`);
        if (!response.ok) throw new Error('Aluno não encontrado.');

        const data = await response.json();

        document.getElementById('currentStudentId').textContent = data.student_info.id;
        document.getElementById('studentMathScore').textContent = data.student_info.math_score.toFixed(2);
        document.getElementById('studentLanguageScore').textContent = data.student_info.language_score.toFixed(2);
        document.getElementById('studentAbsences').textContent = data.student_info.absences;
        document.getElementById('studentParticipation').textContent = data.student_info.participation.toFixed(2);
        document.getElementById('studentHomeworkCompletion').textContent = data.student_info.homework_completion.toFixed(2);
        document.getElementById('studentPreviousPerformance').textContent = data.student_info.previous_performance.toFixed(2);

        renderStudentComparisonChart(data);

    } catch (error) {
        console.error('Erro ao carregar dados do aluno:', error);
        alert('Erro ao carregar dados do aluno.');
    }
}

// Associa o evento click do botão para chamar a função
document.getElementById('loadStudentDataButton').addEventListener('click', loadStudentDashboardData);

document.getElementById('btn-dashboard-main').addEventListener('click', () => {
    document.getElementById('mainDashboard').style.display = 'block';
    document.getElementById('studentDashboard').style.display = 'none';

    document.getElementById('btn-dashboard-main').classList.add('active');
    document.getElementById('btn-dashboard-student').classList.remove('active');
});

document.getElementById('btn-dashboard-student').addEventListener('click', () => {
    document.getElementById('mainDashboard').style.display = 'none';
    document.getElementById('studentDashboard').style.display = 'block';

    document.getElementById('btn-dashboard-student').classList.add('active');
    document.getElementById('btn-dashboard-main').classList.remove('active');
});

