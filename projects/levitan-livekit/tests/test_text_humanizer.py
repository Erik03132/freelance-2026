import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))


from text_humanizer import breath_pcm, count_words, humanize_text


def test_humanize_short_text_untouched():
    assert humanize_text("Менеджер с вами свяжется.") == "Менеджер с вами свяжется."


def test_humanize_already_punctuated_untouched():
    text = "Менеджер свяжется с вами, уточнит заказ и привезёт всё завтра, хорошо?"
    assert humanize_text(text, max_words=10) == text


def test_humanize_inserts_comma_before_marker():
    text = "Инкубатор работает без выходных и мы отправим триста голов уже завтра утром"
    out = humanize_text(text, max_words=8)
    assert "без выходных, и мы" in out


def test_humanize_no_marker_untouched():
    text = "Специально отобранная порода бройлеров растёт очень быстро"
    assert humanize_text(text, max_words=6) == text


def test_humanize_max_commas_cap():
    text = (
        "Один раз привезли партию и потом уточнили адрес когда водитель уже выехал "
        "а потом ещё раз позвонили и спросили про оплату"
    )
    assert humanize_text(text).count(", ") <= 2


def test_humanize_does_not_split_hyphenated_words():
    text = "Менеджер что-то уточнял с водителем и перезвонит вам через десять минут"
    out = humanize_text(text)
    assert "что-то" in out


def test_breath_pcm_format():
    data = breath_pcm(dur=0.2)
    assert len(data) == 0.2 * 48000 * 2
    assert all(len(data) % 2 == 0 for _ in [data])
    samples = [int.from_bytes(data[i : i + 2], "little", signed=True) for i in range(0, 400, 2)]
    assert max(abs(s) for s in samples) > 0


def test_breath_envelope_rises_then_decays():
    data = breath_pcm(dur=0.5)
    sr = 48000

    def win(a, b):
        return max(
            abs(int.from_bytes(data[i : i + 2], "little", signed=True))
            for i in range(a * 2, min(b * 2, len(data)), 200)
        )

    assert win(0, int(0.05 * sr)) < win(int(0.1 * sr), int(0.15 * sr))
    assert win(int(0.4 * sr), int(0.45 * sr)) < win(int(0.1 * sr), int(0.15 * sr))


def test_count_words():
    assert count_words("  Привет, дорогой! ") == 2
    assert count_words("") == 0
