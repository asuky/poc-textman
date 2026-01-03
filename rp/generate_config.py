#!/usr/bin/env python3
"""
Nginxテンプレートファイルのプレースホルダーを置き換えてconf.dに出力するスクリプト
"""
import argparse
import re
from pathlib import Path


def replace_placeholders(template_content, values):
    """
    テンプレート内のプレースホルダー {{VAR_NAME}} を実際の値に置き換える
    
    Args:
        template_content: テンプレートファイルの内容
        values: プレースホルダーと値の辞書
    
    Returns:
        置き換え後の内容
    """
    def replacer(match):
        var_name = match.group(1)
        if var_name in values:
            return values[var_name]
        else:
            print(f"警告: プレースホルダー {var_name} に対応する値が設定されていません")
            return match.group(0)  # 置き換えずにそのまま
    
    # {{VAR_NAME}} 形式のプレースホルダーを置き換え
    pattern = r'\{\{([A-Z_]+)\}\}'
    return re.sub(pattern, replacer, template_content)


def generate_config(template_path, output_path, values):
    """
    テンプレートファイルを読み込み、プレースホルダーを置き換えて出力
    
    Args:
        template_path: テンプレートファイルのパス
        output_path: 出力先ファイルのパス
        values: プレースホルダーと値の辞書
    """
    # テンプレートファイルを読み込む
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # プレースホルダーを置き換え
    config_content = replace_placeholders(template_content, values)
    
    # 出力ディレクトリが存在しない場合は作成
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✓ 設定ファイルを生成しました: {output_path}")


def main():
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(
        description='Nginxテンプレートファイルのプレースホルダーを置き換えてconf.dに出力',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  %(prog)s --fqdn myapp.example.com --target-host-port app:8000
  %(prog)s --fqdn api.example.com --target-host-port backend:8080 --template wordpress.template
        '''
    )
    
    parser.add_argument(
        '--fqdn',
        help='アプリケーションのFQDN（例: app.example.com）'
    )
    
    parser.add_argument(
        '--target-host-port',
        help='バックエンドのホスト:ポート（例: backend:8000）'
    )
    
    parser.add_argument(
        '--wp-fqdn',
        help='WordPressアプリケーションのFQDN（例: wp.example.com）'
    )
    
    parser.add_argument(
        '--wp-host-port',
        help='WordPress PHP-FPMのホスト:ポート（例: wordpress:9000）'
    )
    
    parser.add_argument(
        '--gats-fqdn',
        help='GatsbyアプリケーションのFQDN（例: gatsby.example.com）'
    )
    
    parser.add_argument(
        '--host-ip',
        help='ホストマシンのIPアドレス（例: 192.168.1.100）'
    )
    
    parser.add_argument(
        '--template',
        default='django-with-static.conf.template',
        help='使用するテンプレートファイル名（デフォルト: django-with-static.conf.template）'
    )
    
    parser.add_argument(
        '--output',
        help='出力ファイル名（デフォルト: テンプレート名から.templateを除いたもの）'
    )
    
    args = parser.parse_args()
    
    # スクリプトのディレクトリを基準にパスを設定
    script_dir = Path(__file__).parent
    templates_dir = script_dir / 'templates'
    conf_d_dir = script_dir / 'conf.d'
    
    # プレースホルダーと値の辞書を作成
    values = {}
    
    # 提供された引数のみを辞書に追加
    if args.fqdn:
        values['FQDN'] = args.fqdn
    if args.target_host_port:
        values['TARGET_HOST_PORT'] = args.target_host_port
    if args.wp_fqdn:
        values['WP_FQDN'] = args.wp_fqdn
    if args.wp_host_port:
        values['WP_HOST_PORT'] = args.wp_host_port
    if args.gats_fqdn:
        values['GATS_FQDN'] = args.gats_fqdn
    if args.host_ip:
        values['HOST_IP'] = args.host_ip
    
    print("=== Nginx設定ファイル生成 ===")
    print(f"設定値:")
    for key, value in values.items():
        print(f"  {key} = {value}")
    print()
    
    # テンプレートファイルのパスを設定
    template_file = templates_dir / args.template
    
    # 出力ファイル名を決定
    if args.output:
        output_file = conf_d_dir / args.output
    else:
        # テンプレート名から .template を除去
        output_name = args.template.replace('.template', '.conf') if args.template.endswith('.template') else args.template + '.conf'
        output_file = conf_d_dir / output_name
    
    if template_file.exists():
        generate_config(template_file, output_file, values)
    else:
        print(f"エラー: テンプレートファイルが見つかりません: {template_file}")
        return 1
    
    print("\n完了しました！")
    return 0


if __name__ == '__main__':
    exit(main())
