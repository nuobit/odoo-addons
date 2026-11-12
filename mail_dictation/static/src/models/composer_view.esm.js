/** @odoo-module **/
/* Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {attr} from "@mail/model/model_field";
import {clear} from "@mail/model/model_field_command";
import core from "web.core";
import {registerPatch} from "@mail/model/model_core";

// A recording stops by itself, and is transcribed, at two minutes.
const MAX_SECONDS = 120;

// The formats the recording may take, in order of preference, each with the
// file extension the transcription service reads the format from.
const FORMATS = [
    {extension: "webm", mimeType: "audio/webm"},
    {extension: "ogg", mimeType: "audio/ogg"},
    {extension: "mp4", mimeType: "audio/mp4"},
];

/**
 * Returns the dictated `text` as it goes into `content` between `start` and
 * `end`: with a space before it when the character before the insertion point
 * is not whitespace, and a space after it when the character after it is not.
 *
 * @param {String} text
 * @param {String} content
 * @param {Number} start
 * @param {Number} end
 * @returns {String}
 */
function separateDictation(text, content, start, end) {
    const before = start > 0 && !/\s/.test(content[start - 1]) ? " " : "";
    const after = end < content.length && !/\s/.test(content[end]) ? " " : "";
    return `${before}${text}${after}`;
}

registerPatch({
    name: "ComposerView",
    lifecycleHooks: {
        _willDelete() {
            // A recording holds the microphone, the timer and the Esc
            // listener: it is discarded with the view. A recording already
            // stopped is still transcribed, and its text still delivered to
            // its conversation (_onDictationRecorded).
            if (this.dictationState === "recording") {
                this._discardDictationRecording();
            }
            this._super();
        },
    },
    recordMethods: {
        /**
         * The first click starts recording, the second one stops it and sends
         * the audio for transcription.
         */
        async onClickDictation() {
            switch (this.dictationState) {
                case "idle":
                    await this._startDictation();
                    break;
                case "recording":
                    this._stopDictation();
                    break;
                default:
                    // The button is disabled while the microphone starts and
                    // while the recording is transcribed.
                    throw new Error(
                        `Dictation cannot be toggled while ${this.dictationState}.`
                    );
            }
        },
        /**
         * Listens on the document, in the capture phase, while recording: Esc
         * discards the recording before the composer handles the key.
         *
         * @param {KeyboardEvent} ev
         */
        onKeydownDictation(ev) {
            if (ev.key === "Escape") {
                ev.preventDefault();
                ev.stopPropagation();
                this._discardDictationRecording();
                this.update({
                    dictationInterval: clear(),
                    dictationRecorder: clear(),
                    dictationState: "idle",
                    dictationStream: clear(),
                });
            }
        },
        /**
         * Stops the recorder and releases what the recording holds; the audio
         * recorded so far is never sent.
         *
         * @private
         */
        _discardDictationRecording() {
            const recorder = this.dictationRecorder;
            recorder.ondataavailable = null;
            recorder.onstop = null;
            recorder.stop();
            this._releaseDictation();
        },
        /**
         * @private
         * @param {Error} error the rejection of getUserMedia
         * @returns {String}
         */
        _dictationMicrophoneMessage(error) {
            return ["NotAllowedError", "SecurityError"].includes(error.name)
                ? this.env._t(
                      "Dictation needs the microphone: allow it for this site in the browser and try again."
                  )
                : this.env._t(
                      "The microphone could not be started: check that one is connected and not in use by another program."
                  );
        },
        /**
         * @private
         */
        _onDictationTick() {
            this.update({dictationSeconds: this.dictationSeconds + 1});
            if (this.dictationSeconds === MAX_SECONDS) {
                this._stopDictation();
            }
        },
        /**
         * Puts the text in the box of the dictation's conversation. The text
         * belongs to the conversation where it was recorded, never to whichever
         * box the view shows when it arrives. Nothing is sent to the thread.
         *
         * @private
         * @param {Object} dictation see _startDictation
         * @param {String} text
         */
        _insertDictation({composer, messaging}, text) {
            if (this.exists() && this.composer === composer) {
                // At the cursor, the way an emoji is inserted; a selection is
                // replaced.
                this.saveStateInStore();
                const {textInputContent, textInputCursorEnd, textInputCursorStart} =
                    composer;
                this.insertIntoTextInput(
                    separateDictation(
                        text,
                        textInputContent,
                        textInputCursorStart,
                        textInputCursorEnd
                    )
                );
                if (!messaging.device.isMobileDevice) {
                    this.update({doFocus: true});
                }
            } else if (composer.exists()) {
                // It waits at the end of that conversation's box.
                const {textInputContent} = composer;
                const content =
                    textInputContent +
                    separateDictation(
                        text,
                        textInputContent,
                        textInputContent.length,
                        textInputContent.length
                    );
                composer.update({
                    textInputContent: content,
                    textInputCursorEnd: content.length,
                    textInputCursorStart: content.length,
                });
                for (const composerView of composer.composerViews) {
                    composerView.update({hasToRestoreContent: true});
                }
                messaging.notify({
                    message: messaging.env._t(
                        "The dictated text was added to the conversation where you recorded it."
                    ),
                    type: "info",
                });
            } else {
                messaging.notify({
                    message: messaging.env._t(
                        "The conversation closed before the text arrived; nothing was inserted."
                    ),
                    type: "warning",
                });
            }
        },
        /**
         * Called when the recorder has handed over all its audio. The view may
         * be gone by then, or while the audio is transcribed (a chat window
         * closed): it is only touched while it exists.
         *
         * @private
         * @param {Object} dictation see _startDictation
         * @param {Blob} audio
         */
        async _onDictationRecorded(dictation, audio) {
            if (this.exists()) {
                if (this.dictationState === "recording") {
                    // The recorder stopped by itself: the microphone was
                    // unplugged, or its permission withdrawn.
                    this._releaseDictation();
                }
                this.update({
                    dictationInterval: clear(),
                    dictationRecorder: clear(),
                    dictationState: "transcribing",
                    dictationStream: clear(),
                });
            }
            const data = await this._postDictation(dictation, audio);
            if (this.exists()) {
                this.update({dictationState: "idle"});
            }
            const {messaging} = dictation;
            if ("error" in data) {
                messaging.notify({message: data.error, type: "danger"});
            } else if (data.text) {
                this._insertDictation(dictation, data.text);
            } else {
                messaging.notify({
                    message: messaging.env._t("No words were heard in the recording."),
                    type: "warning",
                });
            }
        },
        /**
         * Posts the recording to the transcription route.
         *
         * @private
         * @param {Object} dictation see _startDictation
         * @param {Blob} audio
         * @returns {Object} the route's answer: {text} or {error}
         */
        async _postDictation({fileName, messaging}, audio) {
            const body = new window.FormData();
            body.append("csrf_token", core.csrf_token);
            body.append("audio", audio, fileName);
            // A request that fails to leave the browser has no response.
            const response = await messaging.browser
                .fetch("/mail_dictation/transcribe", {body, method: "POST"})
                .catch(() => null);
            if (!response) {
                return {
                    error: messaging.env._t(
                        "The server could not be reached. Try again in a moment."
                    ),
                };
            }
            try {
                const data = await response.json();
                if (typeof data.text === "string" || typeof data.error === "string") {
                    return data;
                }
            } catch {
                // Not the route's answer: the login page of an expired session,
                // or an error page.
            }
            return {
                error: messaging.env._t(
                    "The server could not transcribe the recording: reload the page and try again."
                ),
            };
        },
        /**
         * Releases the microphone, the timer and the Esc listener.
         *
         * @private
         */
        _releaseDictation() {
            document.removeEventListener("keydown", this.onKeydownDictation, true);
            this.messaging.browser.clearInterval(this.dictationInterval);
            for (const track of this.dictationStream.getTracks()) {
                track.stop();
            }
        },
        /**
         * @private
         */
        async _startDictation() {
            const {mediaDevices} = this.messaging.browser.navigator;
            const {MediaRecorder} = window;
            const format =
                MediaRecorder &&
                FORMATS.find(({mimeType}) => MediaRecorder.isTypeSupported(mimeType));
            if (!mediaDevices || !format) {
                // Plain http or an old browser offers no recorder.
                this.messaging.notify({
                    message: this.env._t(
                        "This browser cannot record audio here: dictation needs a recent browser and a secure (https) connection."
                    ),
                    type: "danger",
                });
                return;
            }
            this.update({dictationState: "starting"});
            const stream = await mediaDevices
                .getUserMedia({audio: true})
                .catch((error) => {
                    if (this.exists()) {
                        this.update({dictationState: "idle"});
                        this.messaging.notify({
                            message: this._dictationMicrophoneMessage(error),
                            type: "danger",
                        });
                    }
                    return null;
                });
            if (!stream) {
                // The browser gave no microphone; the user has been told why.
                return;
            }
            if (!this.exists()) {
                // The composer was closed while the browser asked for the
                // microphone.
                for (const track of stream.getTracks()) {
                    track.stop();
                }
                return;
            }
            // What the rest of the dictation needs, kept apart from the view,
            // which may be deleted before the text arrives.
            const dictation = {
                // The conversation the text belongs to.
                composer: this.composer,
                fileName: `dictation.${format.extension}`,
                messaging: this.messaging,
            };
            const recorder = new MediaRecorder(stream, {mimeType: format.mimeType});
            const chunks = [];
            recorder.ondataavailable = (ev) => chunks.push(ev.data);
            recorder.onstop = () =>
                this._onDictationRecorded(
                    dictation,
                    new window.Blob(chunks, {type: format.mimeType})
                );
            recorder.start();
            document.addEventListener("keydown", this.onKeydownDictation, true);
            this.update({
                dictationInterval: this.messaging.browser.setInterval(
                    this._onDictationTick,
                    1000
                ),
                dictationRecorder: recorder,
                dictationSeconds: 0,
                dictationState: "recording",
                dictationStream: stream,
            });
        },
        /**
         * Stops recording: the recorder then hands over its audio.
         *
         * @private
         */
        _stopDictation() {
            this._releaseDictation();
            this.update({dictationState: "transcribing"});
            this.dictationRecorder.stop();
        },
    },
    fields: {
        dictationInterval: attr(),
        dictationRecorder: attr(),
        /**
         * Idle, starting (the browser is asked for the microphone), recording
         * or transcribing.
         */
        dictationState: attr({
            default: "idle",
        }),
        dictationSeconds: attr({
            default: 0,
        }),
        dictationStream: attr(),
        /**
         * The recording's length, as minutes and seconds.
         */
        dictationTime: attr({
            compute() {
                const minutes = Math.floor(this.dictationSeconds / 60);
                const seconds = String(this.dictationSeconds % 60).padStart(2, "0");
                return `${minutes}:${seconds}`;
            },
        }),
        dictationTitle: attr({
            compute() {
                switch (this.dictationState) {
                    case "idle":
                        return this.env._t("Dictate");
                    case "starting":
                        return this.env._t("Waiting for the microphone");
                    case "recording":
                        return this.env._t(
                            "Stop and transcribe (Esc discards the recording)"
                        );
                    case "transcribing":
                        return this.env._t("Transcribing");
                    default:
                        throw new Error(
                            `Unknown dictation state: ${this.dictationState}.`
                        );
                }
            },
        }),
        isDictationBusy: attr({
            compute() {
                return ["starting", "transcribing"].includes(this.dictationState);
            },
        }),
    },
});
