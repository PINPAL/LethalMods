const frontendConsole = document.getElementById("console").getElementsByTagName("div")[0];
const progressSteps = document.getElementsByClassName("progressCheck");

const completeSound = new Audio("assets/complete.mp3");
completeSound.volume = 0.2;
const errorSound = new Audio("assets/error.mp3");
errorSound.volume = 0.2;

var totalProgress = 0;

function start() {
	const startButton = document.getElementById("startButton");
	startButton.style.display = "none";

	const mainProgressBar = document.getElementById("mainProgressBar");
	mainProgressBar.style.opacity = 1;
	addToConsole("Starting...", false, true);
	// start the python script
	try {
		eel.pythonMain();
	} catch (error) {
		addToConsole("Error: Python script failed to start.", true);
		addToConsole(error, true);
	}
}

eel.expose(addToConsole); // Expose this function to Python
function addToConsole(text, isError = false, isHeader = false, isSuccess = false) {
	// create elements
	let span = document.createElement("span");
	span.innerHTML = text;
	// add classes if needed
	if (isHeader) {
		span.classList.add("header");
	}
	if (isError) {
		span.classList.add("error");
		errorSound.play();
	}
	if (isSuccess) {
		span.classList.add("success");
		completeSound.play();
	}
	// add to console
	frontendConsole.append(span);
	// scroll to bottom
	frontendConsole.scrollTo(0, frontendConsole.scrollHeight);
}

function updateProgressBar(elementId, progress) {
	let progressBarInner = document.getElementById(elementId).getElementsByClassName("progressBarInner")[0];
	progressBarInner.style.maxWidth = progress + "%";
}
eel.expose(updateDownloadProgress); // Expose this function to Python
function updateDownloadProgress(current, total) {
	console.log(`current: ${current} total: ${total}`);
	if (total > 1) {
		progress = Math.round((current / total) * 100);
		currentMB = Math.round(current / 1024 / 1024);
		totalMB = Math.round(total / 1024 / 1024);
		addToConsole(`Downloading Mods: ${currentMB < 10 ? "0" : ""}${currentMB}/${totalMB} MB     |     ${progress}%`);
		progress = totalProgress + (progress / 100) * (100 / 9);
		updateProgressBar("mainProgressBar", progress);
	} else {
		addToConsole("Downloading Mods: " + currentMB + "MB of Unknown Size");
	}
}

eel.expose(updateProgressText); // Expose this function to Python
function updateProgressText(elementId, inProgress = false) {
	let element = document.getElementById(elementId);
	if (inProgress) {
		element.classList.add("inProgress");
	} else {
		element.classList.add("checked");
		element.classList.remove("inProgress");
	}

	//  loop though each element in progressSteps and check if it has "checked" class
	let progress = 0;
	for (let i = 0; i < progressSteps.length; i++) {
		let element = progressSteps[i];
		if (element.classList.contains("checked")) {
			progress += 1;
		}
	}
	totalProgress = (progress / progressSteps.length) * 100;
	updateProgressBar("mainProgressBar", totalProgress);
}
