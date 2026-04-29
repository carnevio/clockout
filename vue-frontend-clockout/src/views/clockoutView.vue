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

</style>