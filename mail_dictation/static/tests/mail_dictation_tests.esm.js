/** @odoo-module **/
/* Copyright 2026 Xplordoo SL - Eric Antones <eantones@xplordoo.com>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {click, contains} from "@web/../tests/utils";
import {makeDeferred, nextTick, patchWithCleanup} from "@web/../tests/helpers/utils";
import {start, startServer} from "@mail/../tests/helpers/test_utils";
import {browser} from "@web/core/browser/browser";

const {QUnit} = window;

// The recorders and microphone tracks the composer creates during a test.
let recorders = [];
let tracks = [];

/**
 * A recorder that hands over its audio as the browser's does: once stopped,
 * after the current task.
 */
class FakeMediaRecorder {
    static isTypeSupported(mimeType) {
        return mimeType === "audio/webm";
    }

    constructor(stream, {mimeType}) {
        this.mimeType = mimeType;
        this.state = "inactive";
        recorders.push(this);
    }

    start() {
        this.state = "recording";
    }

    stop() {
        this.state = "inactive";
        Promise.resolve().then(() => {
            if (this.ondataavailable) {
                this.ondataavailable({
                    data: new window.Blob(["fake-audio"], {type: this.mimeType}),
                });
            }
            if (this.onstop) {
                this.onstop();
            }
        });
    }
}

QUnit.module("mail_dictation", {
    beforeEach(assert) {
        recorders = [];
        tracks = [];
        patchWithCleanup(window, {MediaRecorder: FakeMediaRecorder}, {pure: true});
        patchWithCleanup(browser.navigator, {
            mediaDevices: {
                async getUserMedia() {
                    assert.step("microphone");
                    const track = {
                        stopped: false,
                        stop() {
                            this.stopped = true;
                        },
                    };
                    tracks.push(track);
                    return {getTracks: () => [track]};
                },
            },
        });
    },
});

/**
 * Opens Discuss on a new channel, answering the transcription route with
 * `answer`.
 *
 * @param {Object} assert
 * @param {Object} answer
 * @returns {Object} what `start` returns
 */
async function openChannel(assert, answer) {
    const pyEnv = await startServer();
    const channelId = pyEnv["mail.channel"].create({name: "General"});
    const result = await start({
        discuss: {context: {active_id: channelId}},
        async mockRPC(route, args) {
            if (route === "/mail_dictation/transcribe") {
                assert.step(`transcribe ${args.body.get("audio").name}`);
                return answer;
            }
            if (route === "/mail/message/post") {
                assert.step("message posted");
            }
        },
    });
    await result.openDiscuss();
    return result;
}

QUnit.test(
    "a click records and the second one puts the text in the box, unsent",
    async function (assert) {
        await openChannel(assert, {text: "Bon dia a tothom"});

        await click(".o_Composer_buttonDictation");
        await contains(".o_Composer_buttonDictation.o-isRecording");
        await click(".o_Composer_buttonDictation");
        await contains(".o_ComposerTextInput_textarea", {value: "Bon dia a tothom"});

        assert.verifySteps(["microphone", "transcribe dictation.webm"]);
        assert.ok(tracks[0].stopped, "should release the microphone");
        await contains(
            ".o_Composer_buttonDictation:not(.o-isRecording):not(:disabled)"
        );
        await contains(".o_Message", {count: 0});
    }
);

QUnit.test("a dictation after a word gets a space before it", async function (assert) {
    const {insertText} = await openChannel(assert, {text: "Bon dia a tothom"});
    await insertText(".o_ComposerTextInput_textarea", "Hola");

    await click(".o_Composer_buttonDictation");
    await contains(".o_Composer_buttonDictation.o-isRecording");
    await click(".o_Composer_buttonDictation");
    await contains(".o_ComposerTextInput_textarea", {value: "Hola Bon dia a tothom"});

    assert.verifySteps(["microphone", "transcribe dictation.webm"]);
});

QUnit.test("a dictation before a word gets a space after it", async function (assert) {
    const {insertText} = await openChannel(assert, {text: "Bon dia a tothom"});
    await insertText(".o_ComposerTextInput_textarea", "món");
    // The cursor at the start of the box.
    document.querySelector(".o_ComposerTextInput_textarea").setSelectionRange(0, 0);

    await click(".o_Composer_buttonDictation");
    await contains(".o_Composer_buttonDictation.o-isRecording");
    await click(".o_Composer_buttonDictation");
    await contains(".o_ComposerTextInput_textarea", {value: "Bon dia a tothom món"});

    assert.verifySteps(["microphone", "transcribe dictation.webm"]);
});

QUnit.test(
    "Esc while recording sends nothing and leaves the box unchanged",
    async function (assert) {
        const {insertText} = await openChannel(assert, {text: "Bon dia a tothom"});
        await insertText(".o_ComposerTextInput_textarea", "Draft");

        await click(".o_Composer_buttonDictation");
        await contains(".o_Composer_buttonDictation.o-isRecording");
        // Esc in the box, where the composer handles it too.
        document
            .querySelector(".o_ComposerTextInput_textarea")
            .dispatchEvent(
                new window.KeyboardEvent("keydown", {bubbles: true, key: "Escape"})
            );
        await contains(".o_Composer_buttonDictation:not(.o-isRecording)");
        await nextTick();

        assert.verifySteps(["microphone"]);
        assert.strictEqual(recorders[0].state, "inactive");
        assert.ok(tracks[0].stopped, "should release the microphone");
        assert.strictEqual(
            document.querySelector(".o_ComposerTextInput_textarea").value,
            "Draft"
        );
    }
);

QUnit.test(
    "an error of the route reaches the user, box unchanged",
    async function (assert) {
        await openChannel(assert, {error: "The transcription service is busy."});

        await click(".o_Composer_buttonDictation");
        await contains(".o_Composer_buttonDictation.o-isRecording");
        await click(".o_Composer_buttonDictation");
        await contains(".o_notification", {text: "The transcription service is busy."});

        assert.verifySteps(["microphone", "transcribe dictation.webm"]);
        assert.strictEqual(
            document.querySelector(".o_ComposerTextInput_textarea").value,
            ""
        );
    }
);

QUnit.test("a browser that cannot record says so", async function (assert) {
    patchWithCleanup(FakeMediaRecorder, {isTypeSupported: () => false}, {pure: true});
    await openChannel(assert, {text: "Bon dia a tothom"});

    await click(".o_Composer_buttonDictation");
    await contains(".o_notification", {
        text: "This browser cannot record audio here: dictation needs a recent browser and a secure (https) connection.",
    });

    assert.verifySteps([]);
    assert.strictEqual(recorders.length, 0);
});

QUnit.test("a refused microphone says so", async function (assert) {
    patchWithCleanup(browser.navigator.mediaDevices, {
        async getUserMedia() {
            assert.step("microphone refused");
            throw new window.DOMException("Permission denied", "NotAllowedError");
        },
    });
    await openChannel(assert, {text: "Bon dia a tothom"});

    await click(".o_Composer_buttonDictation");
    await contains(".o_notification", {
        text: "Dictation needs the microphone: allow it for this site in the browser and try again.",
    });

    assert.verifySteps(["microphone refused"]);
    assert.strictEqual(recorders.length, 0);
    await contains(".o_Composer_buttonDictation:not(.o-isRecording):not(:disabled)");
});

QUnit.test("a recording stops by itself at two minutes", async function (assert) {
    // The intervals the code starts, run by hand second by second.
    const intervals = [];
    patchWithCleanup(browser, {
        setInterval(func, delay) {
            intervals.push({func, delay});
            return intervals.length;
        },
        clearInterval() {
            // The intervals never run by themselves.
        },
    });
    await openChannel(assert, {text: "Bon dia a tothom"});
    intervals.length = 0;

    await click(".o_Composer_buttonDictation");
    await contains(".o_Composer_buttonDictation.o-isRecording");
    assert.strictEqual(intervals.length, 1);
    const [{func: tick, delay}] = intervals;
    assert.strictEqual(delay, 1000);
    for (let second = 1; second < 120; second++) {
        tick();
    }
    await contains(".o_Composer_dictationTime", {text: "1:59"});
    assert.verifySteps(["microphone"]);
    tick();
    await contains(".o_ComposerTextInput_textarea", {value: "Bon dia a tothom"});

    assert.verifySteps(["transcribe dictation.webm"]);
});

/**
 * Starts Discuss on `channelId`, with the transcription route held until the
 * test resolves `answer`.
 *
 * @param {Object} assert
 * @param {Number} channelId
 * @returns {Object} what `start` returns, plus `routeReached` and `answer`
 */
async function startWithHeldRoute(assert, channelId) {
    const routeReached = makeDeferred();
    const answer = makeDeferred();
    const result = await start({
        discuss: {context: {active_id: channelId}},
        async mockRPC(route) {
            if (route === "/mail_dictation/transcribe") {
                assert.step("transcribe");
                routeReached.resolve();
                await answer;
                return {text: "Bon dia a tothom"};
            }
            if (route === "/mail/message/post") {
                assert.step("message posted");
            }
        },
    });
    await result.openDiscuss();
    return {...result, answer, routeReached};
}

QUnit.test(
    "the text goes to the conversation where it was recorded, not to the one shown",
    async function (assert) {
        const pyEnv = await startServer();
        const generalId = pyEnv["mail.channel"].create({name: "General"});
        const randomId = pyEnv["mail.channel"].create({name: "Random"});
        const {answer, insertText, routeReached} = await startWithHeldRoute(
            assert,
            generalId
        );
        await insertText(".o_ComposerTextInput_textarea", "Hola");

        await click(".o_Composer_buttonDictation");
        await contains(".o_Composer_buttonDictation.o-isRecording");
        await click(".o_Composer_buttonDictation");
        await routeReached;
        // Another conversation is shown while the audio is transcribed.
        await click(`.o_DiscussSidebarCategoryItem[data-channel-id="${randomId}"]`);
        await contains(".o_ComposerTextInput_textarea", {value: ""});
        answer.resolve();
        await contains(".o_notification", {
            text: "The dictated text was added to the conversation where you recorded it.",
        });

        assert.strictEqual(
            document.querySelector(".o_ComposerTextInput_textarea").value,
            ""
        );
        await click(`.o_DiscussSidebarCategoryItem[data-channel-id="${generalId}"]`);
        await contains(".o_ComposerTextInput_textarea", {
            value: "Hola Bon dia a tothom",
        });
        assert.verifySteps(["microphone", "transcribe"]);
    }
);

QUnit.test(
    "a conversation closed before the text arrives gets nothing",
    async function (assert) {
        const pyEnv = await startServer();
        const generalId = pyEnv["mail.channel"].create({name: "General"});
        pyEnv["mail.message"].create({
            body: "not empty",
            message_type: "comment",
            model: "mail.channel",
            res_id: generalId,
        });
        const {answer, routeReached} = await startWithHeldRoute(assert, generalId);
        await click(".o_Message");
        await click(".o_MessageActionView_actionEdit");

        await click(".o_Message_composer .o_Composer_buttonDictation");
        await contains(".o_Message_composer .o_Composer_buttonDictation.o-isRecording");
        await click(".o_Message_composer .o_Composer_buttonDictation");
        await routeReached;
        // The edit is cancelled while the audio is transcribed.
        await click(".o_Message_composer a", {text: "cancel"});
        await contains(".o_Message_composer", {count: 0});
        answer.resolve();
        await contains(".o_notification", {
            text: "The conversation closed before the text arrived; nothing was inserted.",
        });

        assert.strictEqual(
            document.querySelector(".o_ComposerTextInput_textarea").value,
            ""
        );
        assert.verifySteps(["microphone", "transcribe"]);
    }
);
