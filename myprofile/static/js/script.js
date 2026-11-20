const input = document.getElementById('terminal-input');
const output = document.getElementById('terminal-output');

const commands = {
    help: "Available commands: <span class='accent'>about</span>, <span class='accent'>skills</span>, <span class='accent'>projects</span>, <span class='accent'>contact</span>, <span class='accent'>clear</span>",
    about: "R. Hemashree — Computer Science & Engineering student & Python/Django Full Stack Developer focused on building practical tools and AI-integrated web apps.",
    skills: "Languages: Python, C, SQL, HTML5, CSS3, JavaScript | Frameworks: Django, Flask, React, Node.js | Tools: Git, MySQL, LaTeX",
    projects: "1. AI Marketplace Platform | 2. Real-Time Currency Analysis Toolkit (Flask + MySQL) | 3. Python Desktop Utility Suite",
    contact: "Reach out via GitHub or LinkedIn, or connect directly through the portfolio contact section."
};

input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
        const cmd = input.value.trim().toLowerCase();
        if (!cmd) return;

        appendLine(`<span class="prompt">guest@hemashree:~$</span> ${cmd}`);

        if (cmd === 'clear') {
            output.innerHTML = '';
        } else if (commands[cmd]) {
            appendLine(commands[cmd]);
        } else {
            appendLine(`Command not found: '${cmd}'. Type <span class="accent">'help'</span> for available commands.`);
        }

        input.value = '';
        output.scrollTop = output.scrollHeight;
    }
});

function appendLine(html) {
    const p = document.createElement('p');
    p.innerHTML = html;
    output.appendChild(p);
}
const copyBtn = document.getElementById('copy-email-btn');
const copyStatus = document.getElementById('copy-status');

if (copyBtn) {
    copyBtn.addEventListener('click', () => {
        const email = copyBtn.getAttribute('data-email');
        navigator.clipboard.writeText(email).then(() => {
            copyStatus.textContent = `Copied ${email} to clipboard!`;
            setTimeout(() => copyStatus.textContent = '', 3000);
        });
    });
}