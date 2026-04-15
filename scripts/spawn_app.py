#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_NAMES = {
    '.git',
    '.build',
    'DerivedData',
    'QuickNoteFinalRehearsal.xcodeproj',
}

TEXT_EXTENSIONS = {
    '.md', '.txt', '.swift', '.yml', '.yaml', '.plist', '.rb', '.py', '.sh', '.json', '.xcconfig', '.gitignore'
}


def slugify(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug or 'new-app'


def app_struct_name(name: str) -> str:
    cleaned = re.sub(r'[^A-Za-z0-9]+', ' ', name)
    return ''.join(part.capitalize() for part in cleaned.split()) or 'NewApp'


def should_skip(path: Path) -> bool:
    return any(part in SKIP_NAMES for part in path.parts)


def copy_template(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    for item in ROOT.iterdir():
        if item.name in SKIP_NAMES:
            continue
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns(*SKIP_NAMES))
        else:
            shutil.copy2(item, target)


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / '.git').exists() and (candidate / 'shared' / 'FoxMountainKit').exists():
            return candidate
    raise RuntimeError('Could not locate the FMS repo root containing shared/FoxMountainKit')


@contextmanager
def pushd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def replace_text(content: str, *, app_name: str, app_slug: str, bundle_id: str, struct_name: str, kit_path: str) -> str:
    replacements = {
        'QuickNoteFinalRehearsal': struct_name,
        'quick note final rehearsal': app_name.lower(),
        'Quick Note Final Rehearsal': app_name,
        'quicknotefinalrehearsal': app_slug.replace('-', ''),
        'dev.foxmountain.quicknotefinalrehearsal': bundle_id,
        'Fox Mountain Quick Note Final Rehearsal': app_name,
        '../../fms/shared/FoxMountainKit': kit_path,
        '../../fms/shared/FoxMountainKit': kit_path,
        '../../fms/shared/FoxMountainKit': kit_path,
        '../../fms/shared/FoxMountainKit': kit_path,
        '../../../fms/shared/FoxMountainKit': kit_path,
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    return content


def apply_release_metadata(destination: Path, metadata: dict) -> None:
    if not metadata:
        return

    appfile = destination / 'fastlane' / 'Appfile'
    if appfile.exists():
        content = appfile.read_text()
        content = re.sub(r'apple_id\(".*?"\)', f'apple_id("{metadata.get("apple_id", "")}")', content)
        content = re.sub(r'team_id\(".*?"\)', f'team_id("{metadata.get("team_id", "")}")', content)
        appfile.write_text(content)

    matchfile = destination / 'fastlane' / 'Matchfile'
    if matchfile.exists():
        content = matchfile.read_text()
        content = re.sub(r'git_url\(".*?"\)', f'git_url("{metadata.get("match_git_url", "")}")', content)
        content = re.sub(r'username\(".*?"\)', f'username("{metadata.get("apple_id", "")}")', content)
        content = re.sub(r'team_id\(".*?"\)', f'team_id("{metadata.get("team_id", "")}")', content)
        matchfile.write_text(content)

    deliverfile = destination / 'fastlane' / 'Deliverfile'
    if deliverfile.exists():
        deliverfile.write_text(
            "# App Store metadata now flows primarily from fms-release.json via fastlane/Fastfile.\n"
            "# Keep this file as a minimal fallback/shim rather than a second source of truth.\n"
            'screenshots_path "./fastlane/screenshots"\n'
        )

    release_contract = destination / 'fms-release.json'
    release_contract.write_text(json.dumps(metadata, indent=2) + "\n")


def customize_spawned_files(destination: Path, *, app_name: str, struct_name: str) -> None:
    readme = destination / 'README.md'
    readme.write_text(
        f'''# {app_name}\n\nGenerated from the Fox Mountain iOS quick note final rehearsal.\n\n## Next Steps\n- Replace the placeholder home screen with the real app experience.\n- Update icons, screenshots, and App Store metadata.\n- Review monetization, analytics, and deployment configuration.\n- Run local generation/build before pushing toward TestFlight.\n\n## Local Commands\n```sh\nxcodegen generate\nxcodebuild -project {struct_name}.xcodeproj -scheme {struct_name} -destination \'generic/platform=iOS Simulator\' build\n```\n'''
    )

    content_view = destination / 'Sources' / 'Views' / 'ContentView.swift'
    content_view.write_text(
        f'''import SwiftUI\nimport FoxMountainKit\n\nstruct ContentView: View {{\n    var body: some View {{\n        TabView {{\n            NavigationStack {{\n                VStack(spacing: 16) {{\n                    Image(systemName: "square.stack.3d.up")\n                        .font(.system(size: 42))\n                        .foregroundStyle(FMColors.accent)\n\n                    Text("{app_name}")\n                        .font(FMFonts.title2)\n                        .multilineTextAlignment(.center)\n\n                    Text("Replace this placeholder screen with the core experience for {app_name}.")\n                        .font(FMFonts.body)\n                        .foregroundStyle(FMColors.textSecondary)\n                        .multilineTextAlignment(.center)\n                        .padding(.horizontal)\n                }}\n                .frame(maxWidth: .infinity, maxHeight: .infinity)\n                .background(FMColors.background)\n                .navigationTitle("Home")\n            }}\n            .tabItem {{\n                Label("Home", systemImage: "house")\n            }}\n\n            NavigationStack {{\n                FMSettingsView(appName: "{app_name}", showPurchaseSection: false) {{\n                    Section("Setup") {{\n                        Text("Configure metadata, branding, monetization, and analytics before release.")\n                    }}\n                }}\n            }}\n            .tabItem {{\n                Label("Settings", systemImage: "gear")\n            }}\n        }}\n    }}\n}}\n\n#Preview {{\n    ContentView()\n}}\n'''
    )


def rewrite_files(destination: Path, *, app_name: str, app_slug: str, bundle_id: str, metadata: dict | None = None) -> None:
    struct_name = app_struct_name(app_name)
    repo_root = find_repo_root(ROOT)
    project_file_base = destination / 'project.yml'
    kit_path = str(Path(shutil.os.path.relpath(repo_root / 'shared' / 'FoxMountainKit', project_file_base.parent)).as_posix())

    for path in destination.rglob('*'):
        if path.is_dir() or should_skip(path):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in {'Fastfile', 'Appfile', 'Deliverfile', 'Matchfile', 'README.md'}:
            try:
                original = path.read_text()
            except UnicodeDecodeError:
                continue
            updated = replace_text(
                original,
                app_name=app_name,
                app_slug=app_slug,
                bundle_id=bundle_id,
                struct_name=struct_name,
                kit_path=kit_path,
            )
            path.write_text(updated)

    src = destination / 'Sources' / 'QuickNoteFinalRehearsal'
    if src.exists():
        renamed = destination / 'Sources' / struct_name
        src.rename(renamed)

    duplicate_content_view = destination / 'Sources' / struct_name / 'ContentView.swift'
    if duplicate_content_view.exists():
        duplicate_content_view.unlink()

    old_test = destination / 'Tests' / 'QuickNoteFinalRehearsalTests.swift'
    if old_test.exists():
        old_test.rename(destination / 'Tests' / f'{struct_name}Tests.swift')

    customize_spawned_files(destination, app_name=app_name, struct_name=struct_name)
    if metadata:
        metadata = dict(metadata)
        metadata.setdefault('app_name', app_name)
        apply_release_metadata(destination, metadata)


def main() -> None:
    parser = argparse.ArgumentParser(description='Spawn a new Fox Mountain app from the template.')
    parser.add_argument('app_name', help='Display name for the new app, e.g. "Unit Converter"')
    parser.add_argument('--destination-root', default=str(find_repo_root(ROOT).parent / 'portfolio-apps'), help='Root folder where the spawned app should be created')
    parser.add_argument('--bundle-id', default=None, help='Explicit bundle identifier, e.g. dev.foxmountain.unitconverter')
    parser.add_argument('--github-org', default='intiharj', help='GitHub org/user for the new repo')
    parser.add_argument('--metadata-json', default=None, help='JSON blob of release metadata for fastlane files')
    parser.add_argument('--private', action='store_true', default=True, help='Create as private repo')
    parser.add_argument('--public', dest='private', action='store_false', help='Create as public repo')
    parser.add_argument('--no-git', action='store_true', help='Skip git initialization and initial commit')
    parser.add_argument('--no-github', action='store_true', help='Skip GitHub repo creation and push')
    args = parser.parse_args()

    app_name = args.app_name.strip()
    app_slug = slugify(app_name)
    bundle_id = args.bundle_id or f'dev.foxmountain.{app_slug.replace("-", "")}'
    destination_root = Path(args.destination_root).expanduser().resolve()
    destination = destination_root / app_slug

    if destination.exists():
        raise SystemExit(f'Destination already exists: {destination}')

    metadata = json.loads(args.metadata_json) if args.metadata_json else None

    copy_template(destination)
    rewrite_files(destination, app_name=app_name, app_slug=app_slug, bundle_id=bundle_id, metadata=metadata)

    repo_name = f'fms-{app_slug}'

    if not args.no_git:
        with pushd(destination):
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Initial spawn of {app_name} from ios-app-template'], check=True)

            if not args.no_github:
                subprocess.run(['gh', 'repo', 'create', f'{args.github_org}/{repo_name}', '--private' if args.private else '--public', '--source=.', '--push'], check=True)
    elif not args.no_github:
        raise SystemExit('--no-github requires git setup unless you also omit --no-git')

    struct_name = app_struct_name(app_name)
    print(f'Spawned quick note final rehearsal at: {destination}')
    print(f'App name: {app_name}')
    print(f'Swift target name: {struct_name}')
    print(f'Bundle ID: {bundle_id}')
    if not args.no_github:
        print(f'GitHub repo: https://github.com/{args.github_org}/{repo_name}')
    else:
        print('GitHub repo: skipped (--no-github)')
    print('Next steps:')
    print(f'  cd {destination}')
    print('  xcodegen generate')
    print(f"  xcodebuild -project {struct_name}.xcodeproj -scheme {struct_name} -destination 'generic/platform=iOS Simulator' build")


if __name__ == '__main__':
    main()
