(function (fileman) {
  function tinymceFilePickerCallback (pickerCallback, value, meta) {
    var win = window.tinymce.activeEditor.windowManager.open({
      url: fileman.TINYMCE_DIALOG_URL,
      width: 600,
      height: 400,
      title: 'Choose file'
    }, {

    });

    // hook into iframe's jquery
    win.$el.find('iframe').on('load', function () {
      var subWindow = win.$el.find('iframe')[0].contentWindow;

      subWindow.$('a.item.file').on('click', function () {
        pickerCallback(this.getAttribute('href'));
        win.close();
        return false;
      });
    });

    // // Provide file and text for the link dialog
    // if (meta.filetype == 'file') {
    //   callback('mypage.html', {text: 'My text'});
    // }
    //
    // // Provide image and alt text for the image dialog
    // if (meta.filetype == 'image') {
    //   callback('myimage.jpg', {alt: 'My alt text'});
    // }
    //
    // // Provide alternative source and posted for the media dialog
    // if (meta.filetype == 'media') {
    //   callback('movie.mp4', {source2: 'alt.ogg', poster: 'image.jpg'});
    // }
  }

  fileman.tinymceFilePickerCallback = tinymceFilePickerCallback;
})(window.fileman);
