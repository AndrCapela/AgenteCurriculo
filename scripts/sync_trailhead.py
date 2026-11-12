"""
Script para sincronizar automaticamente os dados públicos do perfil do Trailhead
com a base de conhecimento do agente (data/knowledge/trailhead.md).
"""

import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime

SLUG = "andrecapela"
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "knowledge" / "trailhead.md"
GRAPHQL_ENDPOINT = "https://profile.api.trailhead.com/graphql"

QUERY = """
query GetFullProfile($slug: String, $hasSlug: Boolean!) {
  profile(slug: $slug) @include(if: $hasSlug) {
    id
    ... on PublicProfile {
      trailheadStats {
        earnedPointsSum
        earnedBadgesCount
        completedTrailCount
        rank {
          title
        }
      }
      earnedSkills {
        skill {
          name
        }
        earnedPointsSum
        itemProgressEntryCount
      }
      credential {
        certifications {
          title
          dateCompleted
          maintenanceDueDate
          status {
            title
            expired
          }
        }
      }
    }
  }
}
"""

def fetch_trailhead_data(slug: str) -> dict:
    payload = json.dumps({
        "query": QUERY,
        "variables": {"slug": slug, "hasSlug": True}
    }).encode("utf-8")

    req = urllib.request.Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def format_date(date_str: str) -> str:
    if not date_str:
        return "N/A"
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            y, m, d = parts[0], parts[1].zfill(2), parts[2].zfill(2)
            return f"{d}/{m}/{y}"
    except Exception:
        pass
    return date_str

def generate_markdown(data: dict, slug: str) -> str:
    profile = data.get("data", {}).get("profile", {})
    stats = profile.get("trailheadStats", {})
    rank = stats.get("rank", {}).get("title", "Ranger")
    points = stats.get("earnedPointsSum", 0)
    badges = stats.get("earnedBadgesCount", 0)
    trails = stats.get("completedTrailCount", 0)
    skills = profile.get("earnedSkills", [])
    certs = profile.get("credential", {}).get("certifications", [])

    # Ordena certificações por data decrescente
    certs_sorted = sorted(certs, key=lambda c: c.get("dateCompleted") or "", reverse=True)

    # Ordena skills por pontuação decrescente
    skills_sorted = sorted(skills, key=lambda s: s.get("earnedPointsSum") or 0, reverse=True)

    lines = []
    lines.append(f"# 🌟 Perfil Oficial Salesforce Trailhead - André Capela")
    lines.append("")
    lines.append(f"- **Link Oficial do Perfil:** https://www.salesforce.com/trailblazer/{slug}")
    lines.append(f"- **Rank no Trailhead:** {rank}")
    lines.append(f"- **Badges Conquistados:** {badges} Badges")
    lines.append(f"- **Pontos Totais:** {points:,} pontos".replace(",", "."))
    lines.append(f"- **Trilhas Completas (Trails):** {trails} trilhas")
    lines.append(f"- **Última Atualização Automática:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## 🏆 Certificações Oficiais Salesforce ({len(certs)}x Certified)")
    lines.append("")
    lines.append("O André possui certificações oficiais da Salesforce, comprovando conhecimento desde o desenvolvimento prático até arquitetura corporativa e Agentforce:")
    lines.append("")

    for idx, c in enumerate(certs_sorted, 1):
        title = c.get("title", "Certificação")
        date_c = format_date(c.get("dateCompleted"))
        status = c.get("status", {}).get("title", "Ativo")
        lines.append(f"{idx}. **{title}**")
        lines.append(f"   - Conclusão: {date_c} | Status: {status}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Habilidades e Competências Práticas (Pontuação Trailhead)")
    lines.append("")
    lines.append("Distribuição das competências e desafios práticos concluídos no Trailhead:")
    lines.append("")

    for s in skills_sorted:
        name = s.get("skill", {}).get("name", "Geral")
        pts = s.get("earnedPointsSum", 0)
        items = s.get("itemProgressEntryCount", 0)
        formatted_pts = f"{pts:,}".replace(",", ".")
        lines.append(f"- **{name}:** {formatted_pts} pontos ({items} módulos concluídos)")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🎯 Principais Diferenciais para Recrutadores e Líderes Técnicos")
    lines.append(f"- **Nível {rank}:** Demonstra consistência, curiosidade técnica e dedicação contínua ao ecossistema Salesforce.")
    lines.append("- **Salesforce Application Architect:** Combina proficiência de código de baixo nível (Apex/LWC) com visão macro de modelagem de dados, arquitetura de integração e segurança.")
    lines.append("- **Pioneirismo em Agentforce & IA:** Possui certificações e especializações em Agentforce, posicionando-se na vanguarda da automação inteligente autônoma dentro da Salesforce.")
    lines.append("")

    return "\n".join(lines)

def main():
    print(f"🔄 Buscando dados públicos de https://www.salesforce.com/trailblazer/{SLUG} ...")
    try:
        data = fetch_trailhead_data(SLUG)
        content = generate_markdown(data, SLUG)
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(content, encoding="utf-8")
        print(f"✅ Sucesso! Base de conhecimento atualizada em: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Erro ao atualizar: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
