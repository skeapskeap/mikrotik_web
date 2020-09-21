$(document).ready(function (){ //метод jQuery ready() начинает работать когда готов DOM, медиа-контент может загружаться позже
    
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

    $("#action_id").change(function() {             //выполняется если в поле action что-то поменялось
        var action = $("#action_id").val();         //узнает, какое значение выбрано в action
        if (action === "new_mac") {                 //если выбрано "поменять мак"
            $("#input_mac").css('display', 'block');//делает свойство css "display"="block" для id=input_mac 
        }

        else {
            $("#input_mac").css('display', 'none');//делает свойство css "display"="none" для id=input_mac 
        }
        
    });

    // Submit post on submit
    $('#def_form').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        do_some();
    });

    // AJAX for posting
    function do_some() {
        console.log("create post is working!") // sanity check
        $.ajax({
            url : "do_some/",   // the endpoint
            type : "POST",      // http method
            data : {            // data sent with the post request
                form_data : $('#def_form').val()
            }, 
            // handle a successful response
            success : function(json) {
                $('#do_some').val(''); // remove the value from the input
                console.log(json); // log the returned json to the console
                $("#result").prepend("<li><strong>"+json.my_text+"</strong> - <a id='delete-post-"+json.del_section+"'>delete me</a></li>");
                console.log("success"); // another sanity check
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

});
