<!doctype html>
<html>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css">
    <title>Laravel File Upload</title>
    <style>
    .container {
        max-width: 500px;

    }

    dl,
    ol,
    ul {
        margin: 0;
        padding: 0;
        list-style: none;
    }
    </style>
</head>

<body>
    <h1>Upload File ke NAS (Synology)</h1>

    @if(session('success'))<p class="success">✅ {{ session('success') }}</p>@endif
    @if($errors->any())<div class="error">
        <ul>@foreach($errors->all() as $e)<li>❌ {{ $e }}</li>@endforeach</ul>
    </div>@endif

    <form action="{{ route('file.upload') }}" method="POST" enctype="multipart/form-data">
        @csrf
        <input type="file" name="file" required>
        <button type="submit">Upload</button>
    </form>

    @if(isset($files) && $files->count())
    <h2>Daftar File</h2>
    <table>
        <thead>
            <tr>
                <th>Nama File</th>
                <th>Relative Path</th>
                <th>Link Publik</th>
            </tr>
        </thead>
        <tbody>
            @foreach($files as $file)
            <tr>
                <td>{{ $file->name }}</td>
                <td>{{ $file->file_path }}</td>
                <td>
                    @if($file->share_url)
                    <a href="{{ $file->share_url }}" target="_blank" rel="noopener">🔗 Buka</a>
                    @else
                    <span style="color:gray">(Belum tersedia)</span>
                    @endif
                </td>
            </tr>
            @endforeach
        </tbody>
    </table>
    @else
    <p>Belum ada file yang diupload.</p>
    @endif

    <h2>Daftar File</h2>
    <ul>
        @foreach($files as $file)
        <li>
            {{ $file->name }}
            | <a href="{{ route('file.download', $file->id) }}">Download</a>
        </li>
        @endforeach
    </ul>
</body>

</html>