$(document).ready(function() {
  
  /*
   * 
   * Uzywac tylko w przypadku AngularJs Material.
   * Na kazdym elemencie .btn, .ripple dodajemy md-ink-ripple by AngularJs Material.
   * Dla .no-ripple nie dodajemy directivy.
   * 
   */  
  
  $(".btn:not(.no-ripple), .ripple").each(function() {
    $(this).attr('md-ink-ripple', '');
  });
  
});
  