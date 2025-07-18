
const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#e67e22'];
let confettiInterval;
let confettiCount = 0;

var playButton = document.getElementById('playButton');
var audioPlayer = document.getElementById('audioPlayer');

document.addEventListener('DOMContentLoaded', function() {
  playButton.addEventListener('click', celebrate);

  function celebrate(){
    playMusic();
    toggleConfetti();
  }

  function playMusic(){
    // Play triumphant music here
    if (audioPlayer.paused) {
        audioPlayer.play();
    } else {
        audioPlayer.pause();
    }
  }


  function toggleConfetti() {
    if (confettiInterval) {
      clearInterval(confettiInterval);
      confettiInterval = null;

      // Remove existing confetti elements
      const existingConfetti = document.querySelectorAll('.confetti');
      existingConfetti.forEach(element => {
        element.remove();
      });
      popup.style.display = 'none';
    } else {
      confettiInterval = setInterval(createConfetti, 150);
      popup.style.display = 'inline-block';
    }
  }

  function createConfetti() {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';
    
    const maxX = window.innerWidth;
    const randomX = Math.random() * maxX;
    const randomColor = colors[Math.floor(Math.random() * colors.length)];

    confetti.style.left = `${randomX}px`;
    confetti.style.backgroundColor = randomColor;

    document.querySelector('.confetti-container').appendChild(confetti);
    confettiCount++;

    confetti.addEventListener('animationend', () => {
      confetti.remove();
      confettiCount--;

      if (confettiCount === 0 && !confettiInterval) {
        clearInterval(confettiInterval);
      }
    });
  }


});




