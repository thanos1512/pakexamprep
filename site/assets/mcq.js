/* Answer-sheet MCQs: tap a bubble, see right/wrong and the explanation, keep score. */
(function () {
  "use strict";

  function setup(set) {
    var questions = Array.prototype.slice.call(set.querySelectorAll(".mcq"));
    var total = questions.length;
    var scoreEl = set.querySelector("[data-score]");
    var answeredEl = set.querySelector("[data-answered]");
    var revealBtn = set.querySelector("[data-reveal]");
    var resetBtn = set.querySelector("[data-reset]");
    var result = null;
    var score = 0;
    var answered = 0;

    if (total > 1) {
      result = document.createElement("div");
      result.className = "result";
      result.hidden = true;
      result.setAttribute("tabindex", "-1");
      set.appendChild(result);
    }

    function update() {
      if (scoreEl) scoreEl.textContent = score;
      if (answeredEl) answeredEl.textContent = answered + " answered";
      if (result && answered === total) showResult();
    }

    function showResult() {
      var missed = questions.filter(function (q) { return q.classList.contains("missed"); });
      var pct = Math.round((score / total) * 100);
      var line;
      if (pct >= 90) line = "Excellent. You know this topic well enough for the paper.";
      else if (pct >= 70) line = "Good work. Revise the ones you missed and try again tomorrow.";
      else if (pct >= 50) line = "A fair start. Read the notes above once more, then retry.";
      else line = "This topic needs another read. Go through the notes, then start again.";
      var html = "<p><strong>You scored " + score + " of " + total + " (" + pct + "%).</strong></p><p>" + line + "</p>";
      if (missed.length) {
        html += "<p>Review: " + missed.map(function (q) {
          var n = q.id.replace("q", "");
          return '<a href="#' + q.id + '">Q' + n + "</a>";
        }).join(", ") + "</p>";
      }
      result.innerHTML = html;
      result.hidden = false;
    }

    function markCorrect(q) {
      var right = q.querySelector('.opt[data-opt="' + q.dataset.answer + '"]');
      if (right) right.classList.add("is-right");
    }

    function lock(q) {
      q.querySelectorAll(".opt").forEach(function (b) { b.disabled = true; });
    }

    questions.forEach(function (q) {
      q.addEventListener("click", function (e) {
        var btn = e.target.closest(".opt");
        if (!btn || q.classList.contains("is-done")) return;
        var good = btn.dataset.opt === q.dataset.answer;
        btn.classList.add("is-picked", good ? "is-right" : "is-wrong");
        btn.setAttribute("aria-pressed", "true");
        if (!good) markCorrect(q);
        q.classList.add("is-done", good ? "got-it" : "missed");
        lock(q);
        answered += 1;
        if (good) score += 1;
        update();
      });
    });

    if (revealBtn) {
      revealBtn.addEventListener("click", function () {
        set.classList.add("is-revealed");
        questions.forEach(function (q) {
          markCorrect(q);
          lock(q);
        });
        revealBtn.disabled = true;
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        set.classList.remove("is-revealed");
        questions.forEach(function (q) {
          q.classList.remove("is-done", "got-it", "missed");
          q.querySelectorAll(".opt").forEach(function (b) {
            b.disabled = false;
            b.classList.remove("is-picked", "is-right", "is-wrong");
            b.removeAttribute("aria-pressed");
          });
        });
        score = 0;
        answered = 0;
        if (result) result.hidden = true;
        if (revealBtn) revealBtn.disabled = false;
        update();
        var first = questions[0];
        if (first) first.scrollIntoView({ block: "start" });
      });
    }

    update();
  }

  document.querySelectorAll(".mcq-set").forEach(setup);
})();
