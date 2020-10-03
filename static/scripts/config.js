$(document).ready(function (){ //метод jQuery ready() начинает работать когда готов DOM, медиа-контент может загружаться позже
    
    $("#add_div").css('display', 'block') // устанавливает дефолтное значение display для раздела добавления пользователя
    $("#mac_div").css('display', 'block')

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
            $("#mac_div").css('display', 'none')
            $("#add_div").css('display', 'none')
        }

        else if (action === "new_mac") {
            $("#ip_div").css('display', 'block');
            $("#mac_div").css('display', 'block');
            $("#add_div").css('display', 'none');
        }

        else {      //if action = 'add'
            $("#ip_div").css('display', 'none')     //делает свойство css "display"="none" для id=ip_div 
            $("#mac_div").css('display', 'block')
            $("#add_div").css('display', 'block')
        }
    });

    // Submit post on submit
    $('form').on('submit', function(event) {
        event.preventDefault()
        $.ajax({
            url: '',
            type: 'post',
            data: $(this).serializeArray(),
            success: function(response) {
                var arp = response.arp
                var dhcp = response.dhcp
                var acl = response.acl
                var message = response.message
                $('#message').text(message[0])
                $("#result").text(message[1])
                
            }
        });
        
        
    });

});
