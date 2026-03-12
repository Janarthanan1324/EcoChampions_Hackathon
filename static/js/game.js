let questions = [];
let currentQuestionIndex = 0;
let score = 0;

// 1. Fetch the data from our Python backend when the page loads
window.onload = async function() {
    try {
        const response = await fetch('/api/questions');
        questions = await response.json();
        
        // Hide loading text and show the quiz
        document.getElementById('loading').style.display = 'none';
        document.getElementById('quiz-content').style.display = 'block';
        
        loadQuestion();
    } catch (error) {
        document.getElementById('loading').innerText = "Error loading missions. Is your Flask server running?";
    }
};

// 2. Display the current question
function loadQuestion() {
    // Reset buttons and hide fact box
    document.getElementById('fact-box').style.display = 'none';
    let btns = document.getElementsByClassName('option-btn');
    for(let btn of btns) {
        btn.disabled = false;
        btn.style.backgroundColor = 'white';
        btn.style.color = '#333';
    }

    let q = questions[currentQuestionIndex];
    document.getElementById('topic-title').innerText = "Mission: " + q.topic;
    document.getElementById('question-text').innerText = q.question;
    document.getElementById('btn-A').innerText = "A) " + q.option_a;
    document.getElementById('btn-B').innerText = "B) " + q.option_b;
    document.getElementById('btn-C').innerText = "C) " + q.option_c;
    document.getElementById('btn-D').innerText = "D) " + q.option_d;
}

// 3. Check the answer
function checkAnswer(selectedOption) {
    let q = questions[currentQuestionIndex];
    let isCorrect = (selectedOption === q.correct_answer);
    
    // Disable all buttons so they can't click twice
    let btns = document.getElementsByClassName('option-btn');
    for(let btn of btns) {
        btn.disabled = true;
    }

    // Highlight the button they clicked
    let selectedBtn = document.getElementById('btn-' + selectedOption);
    if (isCorrect) {
        selectedBtn.style.backgroundColor = '#2ecc71'; // Green for correct
        selectedBtn.style.color = 'white';
        score += parseInt(q.points);
        document.getElementById('current-score').innerText = score;
    } else {
        selectedBtn.style.backgroundColor = '#e74c3c'; // Red for wrong
        selectedBtn.style.color = 'white';
        // Show them the correct one too
        document.getElementById('btn-' + q.correct_answer).style.backgroundColor = '#2ecc71';
        document.getElementById('btn-' + q.correct_answer).style.color = 'white';
    }

    // Show the Fun Fact to guarantee Knowledge Gain!
    document.getElementById('fun-fact-text').innerText = q.fun_fact;
    document.getElementById('fact-box').style.display = 'block';
}

// 4. Move to the next question or end the game
function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        loadQuestion();
    } else {
        // End of game
        document.getElementById('quiz-content').style.display = 'none';
        document.getElementById('end-screen').style.display = 'block';
        document.getElementById('final-score').innerText = score;
    }
}