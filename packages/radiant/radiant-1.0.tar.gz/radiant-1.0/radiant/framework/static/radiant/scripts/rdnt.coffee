



########################################################################
class RDNT

    ##----------------------------------------------------------------------
    #constructor: () ->
        #@DEBUG = true
        #@TIMEOUT = true
        #@TIME_ANIMATION = "0.3s"
        ##@MIN_TIME_ANIMATION = "0s"
        #@WIDTH_DRAWER = $(".mdl-layout__drawer").width() + parseInt($(".mdl-layout__drawer").css("border-right-width")) + parseInt($(".mdl-layout__drawer").css("border-left-width"))


    #----------------------------------------------------------------------
    open_url: (url_) ->

        console.log("open: #{url_}")

        $.get
            data: {"url": url_}
            url: "/RDNT/open_url/"
            success: (response) ->

                if not response.success
                    alert("Error opening #{url_}")



$(document).ready ->

    RDNT = new RDNT()


    $(document).on "click", ".RDNT-open_url", (event) ->

        event.preventDefault()
        url = $(@).attr("href")
        RDNT.open_url(url)



