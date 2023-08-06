Vignette is a library to create and manage thumbnails following the FreeDesktop standard.

Thumbnails are stored in a shared directory so other apps following the standard can reuse
them without having to generate their own thumbnails.

Vignette can typically be used in file managers, image browsers, etc.

Thumbnails are not limited to image files on disk but can be generated for other file types,
for example videos or documents but also for any URL, for example a web browser could store
thumbnails for recently visited pages or bookmarks.

Vignette by itself can only generate thumbnails for local image files but can retrieve
thumbnail for any file or URL, if another app generated a thumbnail for it. An app can also
generate a thumbnail by its own means and use vignette to push that thumbnail to the store.

Vignette has optional support for extra backends like ffmpegthumbnailer, poppler-utils,
ooo-thumbnailer, if these tools are installed.


