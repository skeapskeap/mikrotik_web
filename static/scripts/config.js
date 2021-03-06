$(document).ready(function (){ //метод jQuery ready() начинает работать когда готов DOM, медиа-контент может загружаться позже
    
    $("#data_div").css('display', 'block') // устанавливает дефолтное значение display для раздела добавления пользователя

    function getCookie(name) { //функция парсит document.cookie по аргументу (name='csrftoken') и возвращает значение токена
        var cookieValue = null;

        if (document.cookie && document.cookie !=='') {
            var cookie = document.cookie.split(';');                            //cookie это строка из элементов с ключами и разделителем ';'

            for (var i = 0; i < cookie.length; i++) {                           //проход по списку нарезанному из cookies
                var cookie = cookie[i].trim();                                  //trim аналог strip в python

                if (cookie.substring(0, name.length + 1) === (name + '=')) {    //если найден элемент с ключем (name)
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    var csrfToken = getCookie('csrftoken'); //присваивает в переменную csrfToken результат функции getCookie

    function csrfSafeMethod(method) {       //функция возвращает true для методов !='POST'
        return ['GET', 'OPTIONS', 'HEAD', 'TRACE'].includes(method);
    }

    $.ajaxSetup({                           //функция запихивает csrfToken в http header потому что так круче, чем передавать его внутри POST
        beforeSend: function(xhr, setting) {
            if (!csrfSafeMethod(setting.type) && !this.crossDomain) { //setting.type возвращает метод, в нашем случае POST
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }     
        }
    });

    $("#id_action").change(function() {             //выполняется если в поле action что-то поменялось        
        var action = $("#id_action").val();         //узнает, какое значение выбрано в action  
        if (action === "del") {                     //если выбрано "удалить"
            $("#ip_div").css('display', 'block')    //делает свойство css "display"="block" для id=ip_div 
            $("#data_div").css('display', 'none')
            $(':input','#main_form').not('#id_action').val('')    //очищает все заполненные поля формы кроме action
        }

        else if (action === "update") {    //if action = 'update'
            $("#ip_div").css('display', 'block');
            $("#data_div").css('display', 'block');
            $(':input','#main_form').not('#id_action').val('')    //очищает все заполненные поля формы кроме action
        }

        else {                              //if action = 'add'
            $("#ip_div").css('display', 'none')     //делает свойство css "display"="none" для id=ip_div 
            $("#data_div").css('display', 'block')
            $(':input','#main_form').not('#id_action').val('')    //очищает все заполненные поля формы кроме action
        }
    });

    function displayResponse(response) {
        $("p[id*='error']").empty()   //clear all previous errors
        if (response.form_error) {         // if there is validation error in form
            $('#result').empty()
            $('#message').empty()
            $('#form_error').text(response.form_error["__all__"])
            $('#mac_error').text(response.form_error["mac"])
            $('#ip_error').text(response.form_error["ip"])
            $('#url_error').text(response.form_error["url"])
        }

        else if (response.error) {                   // if there's some backend error
        $('#form_error').empty()
        $('#result').empty()
        $('#message').text(response.error)
        }

        else {                                  // if everything's good
            var message = response.message
            $("#result").empty()                                  //очищает предыдущий вывод
            $(':input','#main_form').not('#id_action').val('')    //очищает все заполненные поля формы кроме action
            $('#message').text(message[0])
            $("#result").append('<p><b>Executed commands:</b></p>')
            for (step = 0; step < message[1].length; step++){
                $('#result').append('<p>&nbsp;&nbsp;&nbsp;' + message[1][step] + '</p>')
            }
        }
    }

    // Submit post on submit
    $('form').on('submit', function(event) {
        event.preventDefault()
        $.ajax({
            url: '',
            type: 'post',
            data: $(this).serializeArray(),
            success: displayResponse
        });
    });

});
