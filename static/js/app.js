const socket = io();
const transcriptionDiv = document.getElementById('transcription');
const batteryStatusDiv = document.getElementById('battery-status'); // Add a reference to battery status div
let currentLineIndex = -1; // To track the current line
let transcriptionLines = []; // Store all transcription lines

// Listen for transcription events
socket.on('transcription', function (data) {
    const result = JSON.parse(data);

    if (result.partial) {  // Handle partial result
        if (currentLineIndex === -1) {
            // If no current line exists, create a new line for partial result
            currentLineIndex = transcriptionLines.length;
            transcriptionLines.push(result.partial); // Add partial to current line
        } else {
            // Update the current line with the partial result
            transcriptionLines[currentLineIndex] = result.partial;
        }
        updateTranscription(); // Update the transcription div with the partial result
    }

    if (result.text) {  // Handle final result
        if (currentLineIndex !== -1) {
            // Replace partial with the final result
            transcriptionLines[currentLineIndex] = result.text;
        } else {
            // If no current line exists, create a new one for the final result
            transcriptionLines.push(result.text);
        }
        currentLineIndex++;  // Move to the next line for the next transcription
        updateTranscription(); // Update the transcription div with the final result
    }
});

// Listen for battery status events
socket.on('battery_status', function (data) {
    if (batteryStatusDiv) {
        batteryStatusDiv.innerText = data.status; // Update the battery status text
    }
});

function updateTranscription() {
    // Clear existing transcription div
    transcriptionDiv.innerHTML = '';

    // Loop through the transcription lines and add them
    transcriptionLines.forEach((line, index) => {
        let lineDiv = document.createElement('div');
        lineDiv.textContent = line.replaceAll("<unk>", "..."); + ".";

        // Add class to make the most recent line white, others gray
        if (index === transcriptionLines.length - 1) {
            lineDiv.classList.add('new-line'); // Most recent line
        } else {
            lineDiv.classList.add('old-line'); // Older lines
        }

        transcriptionDiv.appendChild(lineDiv);
    });

    transcriptionDiv.scrollTop = transcriptionDiv.scrollHeight; // Scroll to the bottom
}

// Clear text function
function clearText() {
    transcriptionLines = []; // Clear transcription data
    currentLineIndex = -1;  // Reset the current line index
    updateTranscription(); // Re-render the empty transcription display
}
