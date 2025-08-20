<!doctype html>
<html>

<head>
    <meta charset="utf-8">
    <title>Upload ke NAS</title>
    <style>
    body {
        font-family: Arial;
        max-width: 900px;
        margin: 32px auto
    }

    .success {
        color: #0a7a0a
    }

    .error {
        color: #b00020
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 20px
    }

    th,
    td {
        border: 1px solid #e5e5e5;
        padding: 8px;
        text-align: left
    }

    th {
        background: #f7f7f7
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

    @foreach($files as $file)
    <p>{{ $file->name }} -
        <a href="{{ $file->share_url }}" target="_blank">Download</a>
    </p>
    @endforeach
</body>

</html>