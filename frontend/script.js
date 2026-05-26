const API_BASE =
"http://127.0.0.1:8000";

let pdfUploaded = false;

let chatHistory = [];

let uploadedFiles = [];


// -------------------------------
// SESSION ID
// -------------------------------

let sessionId =
Date.now().toString() +
Math.random().toString(36).substring(2);

localStorage.setItem(
    "session_id",
    sessionId
);


// -------------------------------
// PDF UPLOAD
// -------------------------------

async function uploadPDF() {

    const files =
        document.getElementById(
            "pdfUpload"
        ).files;

    if (!files.length) return;

    const uploadStatus =
        document.getElementById(
            "uploadStatus"
        );

    uploadStatus.innerHTML =
        "Uploading documents...";

    let successCount = 0;

    try {

        // -------------------------------
        // SEQUENTIAL UPLOAD
        // -------------------------------

        for (const file of files) {

            console.log(
                "UPLOADING:",
                file.name
            );

            const formData =
                new FormData();

            formData.append(
                "file",
                file
            );

            formData.append(
                "session_id",
                sessionId
            );

            const response =
                await fetch(
                    `${API_BASE}/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            console.log(data);

            // -------------------------------
            // FAILED
            // -------------------------------

            if (!response.ok) {

                console.error(data);

                addMessage(

                    `❌ Failed to process "${file.name}"\n\n${data.detail || "Upload failed."}`,

                    "bot"
                );

                continue;
            }

            // -------------------------------
            // SUCCESS
            // -------------------------------

            console.log(
                "SUCCESSFULLY UPLOADED:",
                file.name
            );

            uploadedFiles.push(
                file.name
            );

            successCount++;

            // -------------------------------
            // WAIT BEFORE NEXT UPLOAD
            // -------------------------------

            await new Promise(
                resolve => setTimeout(resolve, 1000)
            );
        }

        renderUploadedFiles();

        if (successCount > 0) {

            pdfUploaded = true;

            uploadStatus.innerHTML =
                `✅ ${successCount} document(s) uploaded`;

        } else {

            uploadStatus.innerHTML =
                "❌ Upload failed";
        }

    } catch (error) {

        console.error(error);

        uploadStatus.innerHTML =
            "❌ Server connection failed";

        addMessage(
            "❌ Unable to connect to backend server.",
            "bot"
        );
    }
}


// -------------------------------
// RENDER FILES
// -------------------------------

function renderUploadedFiles() {

    const container =
        document.getElementById(
            "uploadedFilesContainer"
        );

    if (!container) return;

    if (uploadedFiles.length === 0) {

        container.innerHTML = "";

        return;
    }

    let html =
        `
        <div class="uploaded-files-title">
            Uploaded Documents
        </div>
        `;

    uploadedFiles.forEach(file => {

        html += `
            <div class="uploaded-file-item">
                ✅ ${file}
            </div>
        `;
    });

    container.innerHTML = html;
}


// -------------------------------
// SEND QUESTION
// -------------------------------

async function sendQuestion() {

    const input =
        document.getElementById(
            "questionInput"
        );

    const question =
        input.value.trim();

    if (!question) return;

    addMessage(
        question,
        "user"
    );

    chatHistory.push({

        role: "user",

        content: question
    });

    input.value = "";

    showTyping();

    try {

        const response =
            await fetch(
                `${API_BASE}/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        question:
                            question,

                        history:
                            chatHistory,

                        session_id:
                            sessionId
                    })
                }
            );

        const data =
            await response.json();

        removeTyping();

        if (!response.ok) {

            addMessage(
                `❌ ${data.detail || "Server error"}`,
                "bot"
            );

            return;
        }

        addMessage(
            data.answer,
            "bot"
        );

        chatHistory.push({

            role:
                "assistant",

            content:
                data.answer
        });

    } catch (error) {

        removeTyping();

        console.error(error);

        addMessage(
            "❌ Unable to connect to backend server.",
            "bot"
        );
    }
}


// -------------------------------
// ADD MESSAGE
// -------------------------------

function addMessage(
    text,
    sender
) {

    const chatBox =
        document.getElementById(
            "chatBox"
        );

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(

        sender === "user"
            ? "user-message"
            : "bot-message"
    );

    if (sender === "bot") {

        messageDiv.innerHTML =
            marked.parse(text);

    } else {

        messageDiv.innerText =
            text;
    }

    chatBox.appendChild(
        messageDiv
    );

    smoothScrollToBottom();
}


// -------------------------------
// TYPING INDICATOR
// -------------------------------

function showTyping() {

    const chatBox =
        document.getElementById(
            "chatBox"
        );

    const typingDiv =
        document.createElement("div");

    typingDiv.classList.add(
        "bot-message"
    );

    typingDiv.id =
        "typing-indicator";

    typingDiv.innerHTML =
        `
        <div class="typing-wrapper">

            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>

        </div>
        `;

    chatBox.appendChild(
        typingDiv
    );

    smoothScrollToBottom();
}


function removeTyping() {

    const typingDiv =
        document.getElementById(
            "typing-indicator"
        );

    if (typingDiv) {

        typingDiv.remove();
    }
}


// -------------------------------
// SCROLL
// -------------------------------

function smoothScrollToBottom() {

    const chatBox =
        document.getElementById(
            "chatBox"
        );

    chatBox.scrollTo({

        top:
            chatBox.scrollHeight,

        behavior:
            "smooth"
    });
}


// -------------------------------
// NEW CHAT
// -------------------------------

function clearChat() {

    const chatBox =
        document.getElementById(
            "chatBox"
        );

    chatBox.innerHTML =
        `
        <div class="bot-message">

            <strong>
                New conversation started
            </strong>

            <br><br>

            Upload legal documents and begin chatting.

        </div>
        `;

    chatHistory = [];

    pdfUploaded = false;

    uploadedFiles = [];

    renderUploadedFiles();

    // -------------------------------
    // NEW SESSION
    // -------------------------------

    sessionId =
        Date.now().toString() +
        Math.random().toString(36).substring(2);

    localStorage.setItem(
        "session_id",
        sessionId
    );

    removeSelectedFile();

    document.getElementById(
        "uploadStatus"
    ).innerHTML = "";
}


// -------------------------------
// FILE DISPLAY
// -------------------------------

document
    .getElementById("pdfUpload")
    .addEventListener(

        "change",

        async function() {

            const filePill =
                document.getElementById(
                    "filePill"
                );

            const fileName =
                document.getElementById(
                    "fileName"
                );

            if (
                this.files.length > 0
            ) {

                if (
                    this.files.length === 1
                ) {

                    fileName.innerText =
                        this.files[0].name;

                } else {

                    fileName.innerText =
                        `${this.files.length} files selected`;
                }

                filePill.style.display =
                    "flex";

                await uploadPDF();
            }
        }
    );


// -------------------------------
// REMOVE FILE
// -------------------------------

function removeSelectedFile() {

    const fileInput =
        document.getElementById(
            "pdfUpload"
        );

    fileInput.value = "";

    document.getElementById(
        "filePill"
    ).style.display =
        "none";
}


// -------------------------------
// ENTER KEY
// -------------------------------

document
    .getElementById(
        "questionInput"
    )
    .addEventListener(

        "keydown",

        function(event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendQuestion();
            }
        }
    );