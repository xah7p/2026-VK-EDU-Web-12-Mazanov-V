(function () {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  }

  if (typeof jQuery !== "undefined") {
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !settings.crossDomain) {
          var token = getCookie("csrftoken");
          if (token) {
            xhr.setRequestHeader("X-CSRFToken", token);
          }
        }
      },
    });
  }

  function applyVoteState($block, yourVote) {
    $block.attr(
      "data-user-vote",
      yourVote === 1 ? "1" : yourVote === -1 ? "-1" : "0"
    );
    var $up = $block.find(".js-vote-up");
    var $down = $block.find(".js-vote-down");
    $up.prop("disabled", yourVote === 1);
    $down.prop("disabled", yourVote === -1);
    $up.toggleClass("vote-up-active", yourVote === 1);
    $down.toggleClass("vote-down-active", yourVote === -1);
  }

  function updateVoteCount($block, rating) {
    var $n = $block.find(".js-vote-count");
    $n.text(rating);
    $n.removeClass("vote-count-up vote-count-down");
    if (rating >= 0) {
      $n.addClass("vote-count-up").css("color", "#2b9a79");
    } else {
      $n.addClass("vote-count-down").css("color", "#e90c0c");
    }
  }

  function parseJsonSafe(xhr) {
    try {
      return xhr.responseJSON || JSON.parse(xhr.responseText);
    } catch (e) {
      return null;
    }
  }

  function handleVoteError(xhr, $block) {
    var loginUrl = $block.data("login-url");
    var data = parseJsonSafe(xhr);
    if (xhr.status === 401 && loginUrl) {
      window.location.href = loginUrl;
      return;
    }
    if (xhr.status === 403) {
      alert((data && data.error) || "Доступ запрещён (в т.ч. возможна ошибка CSRF). Обновите страницу.");
      return;
    }
    if (xhr.status === 405) {
      alert((data && data.error) || "Неверный метод запроса.");
      return;
    }
    alert((data && data.error) || "Не удалось выполнить действие.");
  }

  function postVote($block, voteType) {
    var url = $block.data("vote-url");
    if (!url) {
      return;
    }
    jQuery.ajax({
      url: url,
      type: "POST",
      data: { vote_type: voteType },
      success: function (data) {
        if (data && data.ok) {
          updateVoteCount($block, data.rating);
          applyVoteState($block, data.your_vote);
        }
      },
      error: function (xhr) {
        handleVoteError(xhr, $block);
      },
    });
  }

  function postMarkCorrect(answerId) {
    var $meta = jQuery("#mark-correct-endpoint");
    if (!$meta.length) {
      return;
    }
    var url = $meta.data("url");
    if (!url) {
      return;
    }
    jQuery.ajax({
      url: url,
      type: "POST",
      data: { answer_id: answerId },
      success: function (data) {
        if (!data || !data.ok) {
          return;
        }
        jQuery(".js-answer-card .js-correct-badge").hide();
        jQuery(".js-answer-card .js-mark-correct").prop("disabled", false);
        var $card = jQuery('.js-answer-card[data-answer-id="' + data.correct_answer_id + '"]');
        $card.find(".js-correct-badge").show();
        $card.find(".js-mark-correct").prop("disabled", true);
      },
      error: function (xhr) {
        var data = parseJsonSafe(xhr);
        if (xhr.status === 401) {
          var $sample = jQuery(".js-vote-block").first();
          var loginUrl = $sample.data("login-url");
          if (loginUrl) {
            window.location.href = loginUrl;
          } else {
            alert("Требуется вход.");
          }
          return;
        }
        if (xhr.status === 403) {
          alert((data && data.error) || "Доступ запрещён.");
          return;
        }
        if (xhr.status === 405) {
          alert((data && data.error) || "Неверный метод запроса.");
          return;
        }
        alert((data && data.error) || "Не удалось сохранить отметку.");
      },
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (typeof jQuery === "undefined") {
      return;
    }
    jQuery(document).on("click", ".js-vote-up:not(:disabled)", function () {
      postVote(jQuery(this).closest(".js-vote-block"), "like");
    });
    jQuery(document).on("click", ".js-vote-down:not(:disabled)", function () {
      postVote(jQuery(this).closest(".js-vote-block"), "dislike");
    });
    jQuery(document).on("click", ".js-mark-correct:not(:disabled)", function () {
      var aid = jQuery(this).data("answer-id");
      if (aid) {
        postMarkCorrect(aid);
      }
    });
  });
})();
