import json

import outreach


def test_parse_template_splits_subject_and_body():
    subject, body = outreach.parse_template("Asunto: Hola {nombre}\n\nCuerpo {empresa}")
    assert subject == "Hola {nombre}"
    assert body == "Cuerpo {empresa}"


def test_render_raises_on_missing_column():
    try:
        outreach.render("Hola {nombre}", {})
    except ValueError as exc:
        assert "nombre" in str(exc)
    else:  # pragma: no cover - el fallo es el caso esperado
        raise AssertionError("debería haber lanzado ValueError")


def test_read_targets_filters_invalid_and_non_new(tmp_path):
    path = tmp_path / "targets.csv"
    path.write_text(
        "email,nombre,empresa,ciudad,senal,estado\n"
        "a@b.com,Ana,Demo,Bogota,vende bots,nuevo\n"
        "invalido,Beto,X,Y,Z,nuevo\n"
        "c@d.com,Caro,Otra,Cali,hace RAG,enviado\n",
        encoding="utf-8",
    )
    rows = outreach.read_targets(path)
    assert [row["email"] for row in rows] == ["a@b.com"]


def test_draft_writes_one_json_per_valid_target(tmp_path):
    csv_path = tmp_path / "targets.csv"
    csv_path.write_text(
        "email,nombre,empresa,ciudad,senal,estado\n"
        "a@b.com,Ana,Demo,Bogota,vende bots,nuevo\n",
        encoding="utf-8",
    )
    template = tmp_path / "template.txt"
    template.write_text(
        "Asunto: Hola {nombre}\n\nEmpresa: {empresa}\n",
        encoding="utf-8",
    )
    out = tmp_path / "drafts"

    code = outreach.main(
        ["draft", "--csv", str(csv_path), "--template", str(template), "--out", str(out)]
    )

    assert code == 0
    files = list(out.glob("*.json"))
    assert len(files) == 1
    draft = json.loads(files[0].read_text(encoding="utf-8"))
    assert draft["to"] == "a@b.com"
    assert draft["subject"] == "Hola Ana"
    assert "Demo" in draft["body"]


def test_send_without_flag_only_simulates(tmp_path, capsys):
    approved = tmp_path / "approved"
    approved.mkdir()
    (approved / "001-demo.json").write_text(
        json.dumps({"to": "a@b.com", "subject": "Hola", "body": "Texto"}),
        encoding="utf-8",
    )

    code = outreach.main(["send", "--dir", str(approved)])

    assert code == 0
    captured = capsys.readouterr().out
    assert "SIMULACIÓN" in captured
    assert (approved / "001-demo.json").exists()
