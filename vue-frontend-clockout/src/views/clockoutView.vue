<script setup lang="ts">
import { ref } from 'vue';

const selectedFile = ref<File | null>(null);
const base64Result = ref('');
const fileInfo = ref('');
const errorMessage = ref('');
const isConverting = ref(false);
const time = ref('');

type ProcessResponse = {
    end_time?: string;
    times?: unknown;
};

function setClockTime(endTime: string) {
    const date = new Date(endTime);
    time.value = date.toLocaleTimeString('de-DE', {
        hour: '2-digit',
        minute: '2-digit',
    });
}

function setFile(file: File) {
    selectedFile.value = file;
    fileInfo.value = `${file.name} (${file.type || 'unknown type'}, ${file.size} bytes)`;
    base64Result.value = '';
    errorMessage.value = '';
    time.value = '';
}

function onFileInputChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.item(0); // File | null
    if (!file) {
        return;
    }
    setFile(file);
}

async function onPaste(event: ClipboardEvent) {
    const items = event.clipboardData?.items;
    if (!items || items.length === 0) {
        errorMessage.value = 'No clipboard data found. Copy a file and paste again.';
        return;
    }

    for (const item of items) {
        if (item.kind === 'file') {
            const file = item.getAsFile();
            if (file) {
                setFile(file);
                const response = await convertToBase64();
                if (response?.end_time) {
                    setClockTime(response.end_time);
                }
                return;
            }
        }
    }

    errorMessage.value = 'Clipboard does not contain a file. Copy a file or image first.';
}

function convertFileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const result = reader.result;
            if (typeof result !== 'string') {
                reject(new Error('Failed to read file as text data URL.'));
                return;
            }

            const commaIndex = result.indexOf(',');
            if (commaIndex === -1) {
                reject(new Error('Unexpected data URL format.'));
                return;
            }

            resolve(result.slice(commaIndex + 1));
        };
        reader.onerror = () => reject(new Error('Failed to read file.'));
        reader.readAsDataURL(file);
    });
}

async function onSubmit(event: Event) {
    event.preventDefault();
    errorMessage.value = '';

    if (!selectedFile.value) {
        errorMessage.value = 'Choose a file or paste one from clipboard first.';
        return;
    }

    try {
        isConverting.value = true;
        const response = await convertToBase64();
        if (response?.end_time) {
            setClockTime(response.end_time);
        }
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : 'Conversion failed.';
    } finally {
        isConverting.value = false;
    }
}

async function convertToBase64(): Promise<ProcessResponse | null> {
    errorMessage.value = '';

    if (!selectedFile.value) {
        errorMessage.value = 'Choose a file or paste one from clipboard first.';
        return null;
    }

    try {
        isConverting.value = true;
        base64Result.value = await convertFileToBase64(selectedFile.value);
    } catch (error) {
        errorMessage.value = error instanceof Error ? error.message : 'Conversion failed.';
        return null;
    }

    try {
        const response = await fetch('https://api.clockout.ch/process-img', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: base64Result.value,
            }),
        });

        if (!response.ok) {
            errorMessage.value = `Upload failed: ${response.statusText}`;
            return null;
        }

        return (await response.json()) as ProcessResponse;
    } finally {
        isConverting.value = false;
    }
}
</script>

<template>
    <section class="page-shell">
        <div class="page-glow page-glow-left"></div>
        <div class="page-glow page-glow-right"></div>

        <main class="card">
            <header class="hero">
                <p class="eyebrow">Clockout Assistant</p>
                <h2>Modern file processing with a blue interface</h2>
                <p class="subtitle">
                    Paste or upload a file, send it to the backend and get the calculated clock-out time back in a clean, readable view.
                </p>
            </header>

            <form id="new_document_attachment" method="post" @submit="onSubmit" class="form-panel">
                <div class="paste-panel">
                    <label class="field-label" for="paste-target">Or paste a copied file here</label>
                    <textarea
                        id="paste-target"
                        class="paste-target"
                        placeholder="Click here, then paste a file from your clipboard"
                        @paste.prevent="onPaste"
                    />
                </div>

                <div v-if="isConverting" class="loader-wrapper">
                    <div class="loader"></div>
                </div>

                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
            </form>

            <section v-if="time" class="result-block">
                <span class="result-label">Clock-out time</span>
                <p class="info">{{ time }}</p>
            </section>
        </main>
    </section>
</template>

<style scoped>
:global(body) {
    margin: 0;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background:
        radial-gradient(circle at top left, rgba(70, 141, 255, 0.22), transparent 30%),
        radial-gradient(circle at bottom right, rgba(35, 110, 255, 0.14), transparent 26%),
        linear-gradient(180deg, #07111f 0%, #0d1a33 100%);
    color: #eef4ff;
}

.page-shell {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 24px;
    position: relative;
    overflow: hidden;
}

.page-glow {
    position: absolute;
    border-radius: 999px;
    filter: blur(64px);
    pointer-events: none;
    opacity: 0.7;
}

.page-glow-left {
    width: 240px;
    height: 240px;
    left: 6%;
    top: 10%;
    background: rgba(45, 124, 255, 0.28);
}

.page-glow-right {
    width: 280px;
    height: 280px;
    right: 8%;
    bottom: 6%;
    background: rgba(0, 140, 255, 0.18);
}

.card {
    width: min(100%, 760px);
    position: relative;
    z-index: 1;
    padding: 32px;
    border-radius: 28px;
    border: 1px solid rgba(133, 175, 255, 0.18);
    background: rgba(9, 18, 36, 0.78);
    backdrop-filter: blur(18px);
    box-shadow: 0 30px 90px rgba(0, 0, 0, 0.38);
}

.hero {
    margin-bottom: 26px;
}

.eyebrow {
    margin: 0 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.78rem;
    color: #7cb0ff;
}

.hero h2 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3.1rem);
    line-height: 1.05;
    color: #f8fbff;
}

.subtitle {
    margin: 12px 0 0;
    max-width: 62ch;
    color: rgba(232, 241, 255, 0.76);
    line-height: 1.6;
}

.form-panel {
    display: grid;
    gap: 16px;
}

.upload-panel,
.paste-panel {
    display: grid;
    gap: 10px;
}

.field-label {
    font-weight: 600;
    color: #d9e7ff;
}

input[type='file'],
.paste-target {
    width: calc(100% - 32px);
    border: 1px solid rgba(121, 168, 255, 0.22);
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.04);
    color: #f5f8ff;
    padding: 14px 16px;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.paste-target {
    min-height: 126px;
    resize: vertical;
}

input[type='file']::file-selector-button {
    margin-right: 12px;
    border: 0;
    border-radius: 10px;
    padding: 10px 14px;
    background: linear-gradient(135deg, #3a82ff 0%, #185ce0 100%);
    color: white;
    font-weight: 600;
    cursor: pointer;
}

input[type='file']:focus,
.paste-target:focus {
    border-color: rgba(75, 145, 255, 0.95);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.18);
}

.actions {
    margin-top: 6px;
}

.primary-btn {
    border: 0;
    border-radius: 14px;
    padding: 14px 22px;
    background: linear-gradient(135deg, #2e7cff 0%, #1152d8 100%);
    color: #fff;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 12px 28px rgba(18, 88, 219, 0.34);
    transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.primary-btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 16px 32px rgba(18, 88, 219, 0.42);
}

.primary-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.info-card {
    display: grid;
    gap: 4px;
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(72, 119, 214, 0.12);
    border: 1px solid rgba(116, 166, 255, 0.22);
    color: #eff5ff;
}

.info-label,
.result-label {
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #8db8ff;
}

.result-block {
    margin-top: 22px;
    padding: 18px 20px;
    border-radius: 18px;
    border: 1px solid rgba(124, 173, 255, 0.18);
    background: linear-gradient(135deg, rgba(31, 86, 186, 0.18), rgba(11, 21, 41, 0.9));
}

.info {
    margin: 8px 0 0;
    font-size: clamp(1.6rem, 4vw, 2.4rem);
    color: #ffffff;
}

.error {
    margin: 0;
    color: #ffb3c1;
    background: rgba(255, 70, 109, 0.12);
    border: 1px solid rgba(255, 110, 145, 0.18);
    padding: 12px 14px;
    border-radius: 14px;
}

.loader-wrapper {
    display: grid;
    place-items: center;
    margin-top: 8px;
}

@media (max-width: 640px) {
    .card {
        padding: 20px;
        border-radius: 22px;
    }

    .primary-btn {
        width: 100%;
    }
}
/* HTML: <div class="loader"></div> */
.loader {
  width: 50px;
  aspect-ratio: 1;
  border-radius: 50%;
  border: 8px solid #ffffff;
  animation:
    l20-1 0.8s infinite linear alternate,
    l20-2 1.6s infinite linear;
}
@keyframes l20-1{
   0%    {clip-path: polygon(50% 50%,0       0,  50%   0%,  50%    0%, 50%    0%, 50%    0%, 50%    0% )}
   12.5% {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100%   0%, 100%   0%, 100%   0% )}
   25%   {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100% 100%, 100% 100%, 100% 100% )}
   50%   {clip-path: polygon(50% 50%,0       0,  50%   0%,  100%   0%, 100% 100%, 50%  100%, 0%   100% )}
   62.5% {clip-path: polygon(50% 50%,100%    0, 100%   0%,  100%   0%, 100% 100%, 50%  100%, 0%   100% )}
   75%   {clip-path: polygon(50% 50%,100% 100%, 100% 100%,  100% 100%, 100% 100%, 50%  100%, 0%   100% )}
   100%  {clip-path: polygon(50% 50%,50%  100%,  50% 100%,   50% 100%,  50% 100%, 50%  100%, 0%   100% )}
}
@keyframes l20-2{ 
  0%    {transform:scaleY(1)  rotate(0deg)}
  49.99%{transform:scaleY(1)  rotate(135deg)}
  50%   {transform:scaleY(-1) rotate(0deg)}
  100%  {transform:scaleY(-1) rotate(-135deg)}
}

</style>