$(document).ready(function() {

  var $nav = $('.navbar');
  var $body = $('body');
  var $window = $(window);
  var navOffsetTop = $nav.offset().top;
  var $document = $(document);

  function init() {
    $window.on('scroll', onScroll)
    $window.on('resize', resize)
  }

  function resize() {
    $body.removeClass('has-docked-nav')
    navOffsetTop = $nav.offset().top
    onScroll()
  }

  function onScroll() {
    if(navOffsetTop < $window.scrollTop() && !$body.hasClass('has-docked-nav')) {
      $body.addClass('has-docked-nav')
    }
    if(navOffsetTop > $window.scrollTop() && $body.hasClass('has-docked-nav')) {
      $body.removeClass('has-docked-nav')
    }
  }

  init();

});
