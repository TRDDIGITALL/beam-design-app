import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches



# ตั้งค่าฟอนต์สำหรับ matplotlib
plt.rcParams['font.size'] = 9
plt.rcParams['axes.unicode_minus'] = False

# ฟังก์ชันวาดหน้าตัดคาน
def draw_beam_section(b, h, cover, bar_dia, bar_count, stirrup_dia, stirrup_legs, 
                     d_prime=4, bar_dia_comp=None, bar_count_comp=None, stirrup_spacing=15):
    """
    วาดหน้าตัดคานคอนกรีตพร้อมเหล็กเสริม
    """
    # ปรับขนาดให้เหมาะสมกับเว็บและการพิมพ์
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))  # ขนาดเดิม

    # ปรับสเกลให้เป็น cm แทน mm
    b_cm = b/10
    h_cm = h/10
    cover_cm = cover/10
    
    # วาดหน้าตัดคาน
    beam_rect = patches.Rectangle((0, 0), b_cm, h_cm, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.7)
    ax.add_patch(beam_rect)
    
    # วาดเหล็กปลอก
    stirrup_x = cover_cm/2
    stirrup_y = cover_cm/2
    stirrup_w = b_cm - cover_cm
    stirrup_h = h_cm - cover_cm
    stirrup_rect = patches.Rectangle((stirrup_x, stirrup_y), stirrup_w, stirrup_h, 
                                   linewidth=2, edgecolor='red', facecolor='none')
    ax.add_patch(stirrup_rect)

    # คำนวณตำแหน่งเหล็กรับแรงดึง
    if bar_count > 0:
        bar_dia_cm = bar_dia/10  # แปลงเป็น cm
        if bar_count == 1:
            bar_positions = [b_cm/2]
        else:
            clear_span = b_cm - 2*cover_cm - bar_dia_cm
            spacing = clear_span / (bar_count - 1) if bar_count > 1 else 0
            bar_positions = [cover_cm + bar_dia_cm/2 + i*spacing for i in range(bar_count)]
        
        # วาดเหล็กรับแรงดึง
        for x_pos in bar_positions:
            if 0 <= x_pos <= b_cm:
                circle = patches.Circle((x_pos, cover_cm + bar_dia_cm/2), bar_dia_cm/2, 
                                      facecolor='blue', edgecolor='darkblue', linewidth=1)
                ax.add_patch(circle)
    
    # วาดเหล็กรับแรงอัด (ถ้ามี)
    if bar_dia_comp and bar_count_comp and bar_count_comp > 0:
        bar_dia_comp_cm = bar_dia_comp/10  # แปลงเป็น cm
        if bar_count_comp == 1:
            comp_positions = [b_cm/2]
        else:
            clear_span_comp = b_cm - 2*cover_cm - bar_dia_comp_cm
            spacing_comp = clear_span_comp / (bar_count_comp - 1) if bar_count_comp > 1 else 0
            comp_positions = [cover_cm + bar_dia_comp_cm/2 + i*spacing_comp for i in range(bar_count_comp)]
        
        for x_pos in comp_positions:
            if 0 <= x_pos <= b_cm:
                circle = patches.Circle((x_pos, h_cm - cover_cm - bar_dia_comp_cm/2), bar_dia_comp_cm/2, 
                                      facecolor='green', edgecolor='darkgreen', linewidth=1)
                ax.add_patch(circle)

    # เพิ่ม dimensions และ labels
    ax.set_xlim(-1, b_cm+1)
    ax.set_ylim(-1, h_cm+1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Labels ใช้ภาษาอังกฤษ
    ax.text(b_cm/2, -0.5, f'b = {b_cm:.0f} cm', ha='center', va='top', fontsize=9, weight='bold')
    ax.text(-0.5, h_cm/2, f'h = {h_cm:.0f} cm', ha='center', va='center', rotation=90, fontsize=9, weight='bold')
    ax.text(b_cm+0.3, cover_cm + (bar_dia_cm/2 if bar_count > 0 else 0), f'd = {(h_cm-cover_cm):.0f} cm', 
            ha='left', va='center', fontsize=8)
    if bar_dia_comp and bar_count_comp:
        ax.text(b_cm+0.3, h_cm - cover_cm - (bar_dia_comp/10/2 if bar_dia_comp else 0), f"d' = {d_prime/10:.0f} cm", 
                ha='left', va='center', fontsize=8)
    
    # เพิ่มข้อความแสดงรายละเอียดเหล็ก
    steel_type_map = {12: 'DB12', 16: 'DB16', 20: 'DB20', 25: 'DB25', 32: 'DB32'}
    stirrup_type_map = {6: 'RB6', 9: 'RB9', 12: 'DB12'}
    
    tension_steel_name = steel_type_map.get(bar_dia, f'DB{bar_dia}')
    stirrup_steel_name = stirrup_type_map.get(stirrup_dia, f'RB{stirrup_dia}')
    
    # ข้อความรายละเอียดเหล็กรับแรงดึง
    ax.text(b_cm/2, cover_cm - 0.8, f'{bar_count} เส้น {tension_steel_name}', 
            ha='center', va='top', fontsize=8, weight='bold', color='darkblue',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue", alpha=0.8))
    
    # ข้อความรายละเอียดเหล็กรับแรงอัด (ถ้ามี)
    if bar_dia_comp and bar_count_comp:
        comp_steel_name = steel_type_map.get(bar_dia_comp, f'DB{bar_dia_comp}')
        ax.text(b_cm/2, h_cm - cover_cm + 0.8, f'{bar_count_comp} เส้น {comp_steel_name}', 
                ha='center', va='bottom', fontsize=8, weight='bold', color='darkgreen',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen", alpha=0.8))
    
    # ข้อความรายละเอียดเหล็กปลอก
    ax.text(-0.8, h_cm/2, f'{stirrup_steel_name}\n{stirrup_legs} ขา\n@ {stirrup_spacing} cm', 
            ha='center', va='center', fontsize=8, weight='bold', color='darkred',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="lightcoral", alpha=0.8))
    
    # Legend ใช้ภาษาอังกฤษและแสดงรายละเอียดครบ
    legend_elements = [
        patches.Patch(color='blue', label=f'Tension: {bar_count}×{steel_type_map.get(bar_dia, f"DB{bar_dia}")}'),
        patches.Patch(color='red', label=f'Stirrups: {stirrup_steel_name} {stirrup_legs} legs @ {stirrup_spacing} cm'),
    ]
    if bar_dia_comp and bar_count_comp:
        comp_steel_name = steel_type_map.get(bar_dia_comp, f'DB{bar_dia_comp}')
        legend_elements.append(patches.Patch(color='green', label=f'Compression: {bar_count_comp}×{comp_steel_name}'))
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.5, 1), fontsize=7)
    
    ax.set_title('Beam Cross-Section', fontsize=10, weight='bold', pad=10)
    ax.set_xlabel('Width (cm)', fontsize=9)
    ax.set_ylabel('Height (cm)', fontsize=9)
    
    plt.tight_layout()
    return fig

# ฟังก์ชันคำนวณการออกแบบคาน
def calculate_beam_design(fc, fy, b, h, d, Mu, Vu, stirrup_type, stirrup_legs, stirrup_spacing,
                         tension_steel_type, tension_steel_count, compression_steel=False, 
                         compression_steel_type=None, compression_steel_count=None, d_prime=4):
    results = {}
    calculations = []
    
    try:
        # ค่าคงที่
        phi_b = 0.90  # Flexure
        phi_s = 0.75  # Shear
        beta1 = 0.85 if fc <= 280 else max(0.65, 0.85 - 0.05 * (fc - 280) / 70)
        
        calculations.append(f"=== การออกแบบคานคอนกรีต (Strength Design Method) ===")
        calculations.append(f"• ข้อมูลพื้นฐาน: $f'_c$ = {fc} kg/cm², $f_y$ = {fy} kg/cm²\\")
        calculations.append(f"• ขนาดคาน: b = {b} cm, h = {h} cm, d = {d} cm\\")
        calculations.append(f"• $β_1$ = {beta1:.3f}\\")
        
        # คำนวณ ρmin และ ρmax (แก้ไขตาม ACI 318)
        rho_min = max(1.4 / fy, 0.8 * math.sqrt(fc) / fy)
        rho_max = 0.75 * (0.85 * fc / fy) * (beta1 / (1 + beta1))  # แก้ไขสูตร
        
        calculations.append(f"• $ρ_{{min}}$ = max($\\frac{{1.4}}{{f_y}}$, $\\frac{{0.8\\sqrt{{f'_c}} }}{{f_y}}$) = {rho_min:.4f}\\")
        calculations.append(f"• $ρ_{{max}} = 0.75× 0.85 β_1  \\frac{{f'_c}}{{f_y}}\\cdot  \\frac{{6120}}{{6120+f_y}}$ = {rho_max:.4f} (ACI 318)\\")
        
        # คำนวณพื้นที่เหล็กที่ต้องการ (แก้ไขการคำนวณ Rn และหน่วยให้ถูกต้อง)
        # แปลงหน่วย: Mu (kg-m) → N-mm
        Mu_N_mm = Mu * 9.81 * 1000  # kg-m → N-mm (1 kg = 9.81 N, 1 m = 1000 mm)
        b_mm = b * 10  # cm → mm
        d_mm = d * 10  # cm → mm
        
        Rn = Mu_N_mm / (phi_b * b_mm * d_mm**2)  # N/mm² (หน่วยถูกต้อง)
        
        # ใช้สูตรง่าย ρ = Rn/fy สำหรับคานเหล็กเดี่ยว
        rho_required = Rn / fy
            
        As_required = rho_required * b * d
        
        calculations.append(f"• การแปลงหน่วย: $M_u$ = {Mu} kg-m = {Mu_N_mm:,.0f} N-mm\\")
        calculations.append(f"• $R_n = \\frac{{M_u}}{{\phi  b  d²}}$ ")
        calculations.append(f" = $\\frac{{ {Mu_N_mm:,.0f} }} {{ 0.9×{b_mm}×{d_mm}²}}$ = {Rn:.2f} N/mm²\\")
        calculations.append(f"• $ρ_{{required}} = \\frac{{R_n}}{{f_y }} $ = {Rn:.2f}/{fy} = {rho_required:.6f}\\")
        calculations.append(f"• $A_{{s~required}}$ = {As_required:.2f} cm²\\")
        
        # ตรวจสอบข้อกำหนด ρ (แก้ไขการเปรียบเทียบ)
        rho_status = "OK"
        if rho_required < rho_min:
            rho_status = "ใช้ $ρ_{{min}}$ เนื่องจาก ρ < $ρ_{{min}}$"
            rho_required = rho_min
            As_required = rho_min * b * d
            calculations.append(f"• เนื่องจาก $ρ_{{required}}$ = {Rn/fy:.6f} < $ρ_{{min}}$ = {rho_min:.4f}\\")
            calculations.append(f"• ดังนั้นใช้ $ρ = ρ_{{min}}$ = {rho_min:.4f}\\")
            calculations.append(f"• $A_{{s,required}} = ρ_{{min}} b d$ = {rho_min:.4f}×{b}×{d} = {As_required:.2f} cm²\\")
        elif rho_required > rho_max:
            rho_status = "เกิน $ρ_{{max}}$ - ต้องใช้เหล็กรับแรงอัด"
            
        calculations.append(f"• ตรวจสอบ: $ρ_{{min}}$ = {rho_min:.4f} ≤ ρ = {rho_required:.4f} ≤ $ρ_{{max}}$ = {rho_max:.4f} → {rho_status}")
        
        # คำนวณเหล็กที่จัดให้
        steel_areas = {'DB12': 1.13, 'DB16': 2.01, 'DB20': 3.14, 'DB25': 4.91, 'DB32': 8.04}
        As_provided_tension = steel_areas[tension_steel_type] * tension_steel_count
        
        calculations.append(f"\n--- เหล็กรับแรงดึง ---" )
        calculations.append(f"• เลือกใช้: {tension_steel_count} เส้น {tension_steel_type}\\")
        calculations.append(f"• $A_{{s,provided}}$ = {As_provided_tension:.2f} cm²\\")
        calculations.append(f"• ตรวจสอบ: $A_{{s,provided}}$ = {As_provided_tension:.2f} {'≥' if As_provided_tension >= As_required else '<'} As required = {As_required:.2f} cm² → {'ผ่าน' if As_provided_tension >= As_required else 'ไม่ผ่าน'}\\")
        
        # คำนวณ Mn แบบละเอียดและถูกต้อง (แยกคำนวณแรงดึงและแรงอัด)
        As_prime = 0
        if compression_steel and compression_steel_count > 0:
            As_prime = steel_areas[compression_steel_type] * compression_steel_count
            calculations.append(f"\n--- เหล็กรับแรงอัด ---")
            calculations.append(f"• เลือกใช้: {compression_steel_count} เส้น {compression_steel_type}\\")
            calculations.append(f"• As' = {As_prime:.2f} cm²\\")
        
        # คำนวณ a และ Mn ถูกต้องตาม ACI 318 (แก้ไขให้ละเอียดและถูกต้อง)
        a = (As_provided_tension * fy) / (0.85 * fc * b)  # ไม่ลบ As' เพราะคิดแยก
        
        # ตรวจสอบ a ≤ 0.75d สำหรับ Under-reinforced section
        a_max = 0.75 * d
        calculations.append(f"• ตรวจสอบ a = {a:.2f} cm {'≤' if a <= a_max else '>'} 0.75d = {a_max:.2f} cm → {'Under-reinforced' if a <= a_max else 'Over-reinforced'} ")
        
        # คำนวณ Mn โดยรวมทั้งแรงดึงและแรงอัด
        Mn_tension = As_provided_tension * fy * (d - a/2)  # โมเมนต์จากเหล็กรับแรงดึง (kg-cm)
        Mn_compression = As_prime * fy * (d - d_prime)     # โมเมนต์จากเหล็กรับแรงอัด (kg-cm)
        Mn_total_kg_cm = Mn_tension + Mn_compression       # รวม (kg-cm)
        Mn = Mn_total_kg_cm / 100                          # แปลงเป็น kg-m
            
        phi_Mn = phi_b * Mn
        
        calculations.append(f"\n--- การคำนวณ Mn (แก้ไขให้ถูกต้อง) ---")
        calculations.append(f"• $a = \\frac{{A_s×f_y}}{{0.85×f'_c×b}}$ = {As_provided_tension:.3f}×{fy}/(0.85×{fc}×{b}) = {a:.2f} cm\\")
        calculations.append(f"• $M_{{n,tension}} = A_s f_y (d-\\frac{{a}}{{2}})$ = {As_provided_tension:.3f}×{fy}×({d}-{a:.2f}/2)\\")
        calculations.append(f" $~~~~~~~~~~~~~~~$= {As_provided_tension:.3f}×{fy}×{d-a/2:.2f} = {Mn_tension:,.0f} kg-cm\\")
        if As_prime > 0:
            calculations.append(f"• Mn_compression = As'×fy×(d-d') = {As_prime}×{fy}×({d}-{d_prime})\\")
            calculations.append(f"              = {As_prime}×{fy}×{d-d_prime} = {Mn_compression:,.0f} kg-cm\\")
        calculations.append(f"• $M_{{n,total}}$ = {Mn_tension:,.0f} + {Mn_compression:,.0f} = {Mn_total_kg_cm:,.0f} kg-cm\\")
        calculations.append(f"• $M_n$ = {Mn_total_kg_cm:,.0f}/100 = {Mn:,.0f} kg-m\\")
        calculations.append(f"• $\phi M_n$ = {phi_b}×{Mn:,.0f} = {phi_Mn:,.0f} kg-m\\")
        calculations.append(f"• ตรวจสอบ: $\phi M_n$ = {phi_Mn:,.0f} {'≥' if phi_Mn >= Mu else '<'} $M_u$ = {Mu:,.0f} kg-m → {'ผ่าน' if phi_Mn >= Mu else 'ไม่ผ่าน'}")
        
        # คำนวณแรงเฉือน (แก้ไขสูตร Vc ตาม ACI 318)
        calculations.append(f"\n--- การตรวจสอบแรงเฉือน ---")
        Vc = 0.53 * math.sqrt(fc) * b * d  # kg (สูตร ACI 318)
        phi_Vc = phi_s * Vc
        
        calculations.append(f"• $V_c = 0.53\\sqrt{{f'_c}} b d = 0.53\sqrt{{ {fc} }}×{b}×{d}$ = {Vc:,.0f} kg (ACI 318)\\")
        calculations.append(f"• $\phi V_c$ = {phi_s}×{Vc:.0f} = {phi_Vc:.0f} kg\\")
        calculations.append(f"• ตรวจสอบ: $\phi V_c$ = {phi_Vc:.0f} {'≥' if phi_Vc >= Vu else '<'} $V_u$ = {Vu} kg → {'ผ่าน' if phi_Vc >= Vu else 'ไม่ผ่าน'}")
        
        # ตรวจสอบเหล็กปลอก
        stirrup_areas = {'RB6': 0.283, 'RB9': 0.636, 'DB12': 1.131}
        Av = stirrup_areas[stirrup_type] * stirrup_legs
        max_spacing = min(d/2, 60)  # cm
        
        calculations.append(f"\n--- เหล็กปลอก ---")
        calculations.append(f"• เลือกใช้: {stirrup_type} จำนวน {stirrup_legs} ขา\\")
        calculations.append(f"• $A_v$ = {Av:.3f} cm²\\")
        calculations.append(f"• ระยะเรียง = {stirrup_spacing} cm\\")
        calculations.append(f"• ระยะเรียงสูงสุดที่อนุญาต = min( $\\frac{{d}}{{2}}$, 60) = {max_spacing:.0f} cm\\")
        calculations.append(f"• ตรวจสอบ: {stirrup_spacing} {'≤' if stirrup_spacing <= max_spacing else '>'} {max_spacing:.0f} cm → {'ผ่าน' if stirrup_spacing <= max_spacing else 'ไม่ผ่าน'}")
        
        # สรุปผล
        calculations.append(f"\n=== สรุปผลการออกแบบ ===")
        moment_check = phi_Mn >= Mu
        shear_check = phi_Vc >= Vu
        tension_steel_adequate = As_provided_tension >= As_required
        stirrup_adequate = stirrup_spacing <= max_spacing
        rho_check = rho_required <= rho_max
        
        # เพิ่มการแจ้งปัญหาอย่างละเอียด
        problems = []
        if not moment_check:
            problems.append(f"❌ โมเมนต์: $\phi M_n$ = {phi_Mn:,.0f} < $M_u$ = {Mu:,.0f} kg-m")
        if not shear_check:
            problems.append(f"❌ แรงเฉือน: $\phi V_c$ = {phi_Vc:,.0f} < $V_u$ = {Vu:,.0f} kg")
        if not tension_steel_adequate:
            problems.append(f"❌ เหล็กรับแรงดึงไม่พอ: $A_s$ = {As_provided_tension:.2f} < {As_required:.2f} cm² (ขาด {As_required-As_provided_tension:.2f} cm²)")
        if not stirrup_adequate:
            problems.append(f"❌ เหล็กปลอก: ระยะเรียง {stirrup_spacing} > {max_spacing:.0f} cm")
        if not rho_check:
            problems.append(f"❌ ρ เกิน: ρ = {rho_required:.4f} > $\rho_{{max}}$ = {rho_max:.4f} (เกิน {((rho_required/rho_max-1)*100):.1f}%)")
            
        if problems:
            calculations.append(f"\n🔴 ปัญหาที่พบ:")
            for problem in problems:
                calculations.append(f"  {problem}")
                
            calculations.append(f"\n💡 แนวทางแก้ไข:")
            if not rho_check:
                calculations.append(f"  1. เพิ่มขนาดคาน (แนะนำ: b×h = {int(b*1.2)}×{int(h*1.2)} cm)")
                calculations.append(f"  2. เพิ่มเหล็กรับแรงอัด")
            if not tension_steel_adequate:
                need_bars = math.ceil(As_required / steel_areas[tension_steel_type])
                calculations.append(f"  3. เพิ่มเหล็กรับแรงดึงเป็น {need_bars} เส้น {tension_steel_type}")
                
        results.update({
            'As_required': As_required,
            'As_provided_tension': As_provided_tension,
            'As_prime': As_prime,
            'rho_required': rho_required,
            'rho_min': rho_min,
            'rho_max': rho_max,
            'rho_status': rho_status,
            'Mn': Mn,
            'phi_Mn': phi_Mn,
            'Vc': Vc,
            'phi_Vc': phi_Vc,
            'Av': Av,
            'moment_check': moment_check,
            'shear_check': shear_check,
            'tension_steel_adequate': tension_steel_adequate,
            'stirrup_adequate': stirrup_adequate,
            'rho_check': rho_check
        })
        
        results['design_ok'] = all([
            moment_check,
            shear_check,
            tension_steel_adequate,
            stirrup_adequate,
            rho_check
        ])
        
    except Exception as e:
        results['error'] = str(e)
        results['design_ok'] = False
        calculations.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    results['calculations'] = calculations
    return results

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="โปรแกรมออกแบบคานคอนกรีต", 
    page_icon="🏗️",
    layout="wide"
)

# CSS สำหรับการพิมพ์
st.markdown("""
<style>
@media print {
    .stApp {
        margin: 0;
        padding: 0;
    }
    .stSidebar {
        display: none !important;
    }
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
        margin: 0;
    }
    .metric-container {
        background: white !important;
        border: 1px solid #ccc;
        padding: 0.5rem;
        margin: 0.25rem;
    }
    .element-container {
        page-break-inside: avoid;
    }
    .calculations-section {
        page-break-before: auto;
        page-break-after: auto;
    }
    .stButton {
        display: none !important;
    }
    .stSelectbox, .stNumberInput, .stCheckbox {
        display: none !important;
    }
    .stExpander {
        border: 1px solid #ccc !important;
        margin: 0.05rem 0 !important;
        page-break-inside: avoid;
    }
    .stExpander > div > div {
        padding: 0.2rem !important;
        font-size: 8px !important;
        line-height: 1.0 !important;
    }
    .stTextArea {
        display: none !important;
    }
    h1, h2, h3, h4 {
        color: black !important;
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
        font-size: 14px !important;
    }
    .dataframe {
        font-size: 8px;
    }
    .stPlotlyChart {
        height: 300px !important;
    }
}
.print-optimized {
    font-size: 12px;
    line-height: 1.2;
}
@page {
    size: A4 portrait;
    margin: 1.0cm;
}
</style>
""", unsafe_allow_html=True)

# หัวข้อหลัก
st.title("🏗️ โปรแกรมออกแบบคานคอนกรีต - Strength Design Method")
st.markdown("**Concrete Beam Design using Strength Design Method (SDM)**")

# ปุ่มพิมพ์ (แสดงเฉพาะเมื่อมีผลลัพธ์)
col_title1, col_title2 = st.columns([3, 1])
with col_title2:
    if st.button("🖨️ พิมพ์รายงาน", help="กด Ctrl+P หรือ Cmd+P หลังจากกดปุ่มนี้"):
        st.success("✅ กรุณากด Ctrl+P (Windows) หรือ Cmd+P (Mac) เพื่อพิมพ์")

# Sidebar สำหรับ Input
st.sidebar.header("📝 ข้อมูลการออกแบบ")

# 1. คุณสมบัติวัสดุ
st.sidebar.subheader("1. คุณสมบัติวัสดุ")
fc = st.sidebar.number_input("กำลังอัดคอนกรีต $f'_c$ (kg/cm²)", min_value=150, max_value=500, value=240, step=10)
fy = st.sidebar.number_input("กำลังดึงเหล็ก $f_y$ (kg/cm²)", min_value=2400, max_value=4200, value=4000, step=200)

# 2. ขนาดหน้าตัด
st.sidebar.subheader("2. ขนาดหน้าตัด")
b = st.sidebar.number_input("ความกว้าง b (cm)", min_value=20, max_value=100, value=30, step=5)
h = st.sidebar.number_input("ความสูง h (cm)", min_value=30, max_value=150, value=50, step=5)
cover = st.sidebar.number_input("ระยะคอนกรีตปก cover (cm)", min_value=2, max_value=8, value=4, step=1)

# 3. แรงกระทำ
st.sidebar.subheader("3. แรงกระทำ")
Mu = st.sidebar.number_input("โมเมนต์ดัดใช้งาน $M_u$ (kg-m)", min_value=1000, max_value=50000, value=5500, step=100)
Vu = st.sidebar.number_input("แรงเฉือนใช้งาน $V_u$ (kg)", min_value=1000, max_value=20000, value=3257, step=50)

# 4. เหล็กปลอก
st.sidebar.subheader("4. เหล็กปลอก (Stirrups)")
stirrup_type = st.sidebar.selectbox("เลือกเหล็กปลอก", ["RB6", "RB9", "DB12"])
stirrup_legs = st.sidebar.number_input("จำนวนขา", min_value=2, max_value=6, value=2, step=1)
stirrup_spacing = st.sidebar.number_input("ระยะเรียง (cm)", min_value=5, max_value=30, value=15, step=1)

# 5. เหล็กรับแรงดึง
st.sidebar.subheader("5. เหล็กรับแรงดึง")
tension_steel_type = st.sidebar.selectbox("เลือกขนาดเหล็กรับแรงดึง", ["DB12", "DB16", "DB20", "DB25", "DB32"])
tension_steel_count = st.sidebar.number_input("จำนวนเส้นเหล็กรับแรงดึง", min_value=1, max_value=10, value=3, step=1)

# 6. เหล็กรับแรงอัด (เลือกได้)
st.sidebar.subheader("6. เหล็กรับแรงอัด (เลือกได้)")
compression_steel = st.sidebar.checkbox("ใช้เหล็กรับแรงอัด")
compression_steel_type = "DB16"
compression_steel_count = 0
d_prime = 4

if compression_steel:
    compression_steel_type = st.sidebar.selectbox("เลือกขนาดเหล็กรับแรงอัด", ["DB12", "DB16", "DB20", "DB25", "DB32"], key="comp_steel")
    compression_steel_count = st.sidebar.number_input("จำนวนเส้นเหล็กรับแรงอัด", min_value=0, max_value=8, value=2, step=1)
    d_prime = st.sidebar.number_input("ระยะ d' (cm)", min_value=2, max_value=10, value=4, step=1)

# ปุ่มคำนวณ
calculate = st.sidebar.button("🚀 คำนวณ", type="primary")

# Main Content
if calculate:
    # ส่งค่าพารามิเตอร์เพิ่มเติม
    if compression_steel:
        results = calculate_beam_design(fc, fy, b, h, h-cover, Mu, Vu, stirrup_type, stirrup_legs, stirrup_spacing,
                                      tension_steel_type, tension_steel_count, compression_steel, 
                                      compression_steel_type, compression_steel_count, d_prime)
    else:
        results = calculate_beam_design(fc, fy, b, h, h-cover, Mu, Vu, stirrup_type, stirrup_legs, stirrup_spacing,
                                      tension_steel_type, tension_steel_count)
    
    # ===== หน้าที่ 1: ข้อมูลโครงการและผลลัพธ์หลัก =====
    st.markdown('<div class="print-optimized">', unsafe_allow_html=True)
    
    # Header สำหรับการพิมพ์
    st.markdown("---")
    col_header1, col_header2 = st.columns([2, 1])
    with col_header1:
        st.markdown("### 📋 รายงานการออกแบบคานคอนกรีต")
        st.markdown(f"**วันที่:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
    with col_header2:
        st.markdown("**หน้า 1/1**")
    
    # ข้อมูลโครงการ
    st.markdown("#### 📐 ข้อมูลการออกแบบ")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        **คุณสมบัติวัสดุ:**
        - $f'_c$ = {fc} kg/cm²
        - $f_y$ = {fy} kg/cm²
        """)
        
    with col2:
        st.markdown(f"""
        **ขนาดคาน:**
        - b = {b} cm
        - h = {h} cm  
        - d = {h-cover} cm
        - cover = {cover} cm
        """)
        
    with col3:
        st.markdown(f"""
        **แรงกระทำ:**
        - $M_u$ = {Mu:,.0f} kg-m
        - $V_u$ = {Vu:,.0f} kg
        """)
    
    # ผลลัพธ์หลัก (ขนาดใหญ่ขึ้นสำหรับการพิมพ์)
    st.markdown("#### 🎯 ผลลัพธ์การออกแบบ")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric(
            "$A_s$ ที่ต้องการ", 
            f"{results.get('As_required', 0):.2f} cm²",
            delta=f"ρ = {results.get('rho_required', 0):.4f}"
        )
        
    with col2:
        st.metric(
            "$\phi M_n$", 
            f"{results.get('phi_Mn', 0):,.0f} kg-m",
            delta="✅ ผ่าน" if results.get('moment_check', False) else "❌ ไม่ผ่าน"
        )
        
    with col3:
        st.metric(
            "$\phi V_c$", 
            f"{results.get('phi_Vc', 0):,.0f} kg",
            delta="✅ ผ่าน" if results.get('shear_check', False) else "❌ ไม่ผ่าน"
        )
    
    # สรุปการตรวจสอบ (แบบตาราง)
    st.markdown("#### 📋 สรุปการตรวจสอบ")
    
    check_data = {
        'รายการตรวจสอบ': [
            'โมเมนต์ดัด ($\phi M_n \ge M_u$)',
            'แรงเฉือน ($\phi V_c$ ≥ Vu)', 
            'เหล็กรับแรงดึง ($A_s$ ≥ $A_{{s,req}}$)',
            'เหล็กปลอก (spacing ≤ max)',
            'อัตราเหล็ก (ρ ≤ $\\rho_{{max}}$)'
        ],
        'ค่าที่ได้': [
            f"{results.get('phi_Mn', 0):,.0f} kg-m",
            f"{results.get('phi_Vc', 0):,.0f} kg",
            f"{results.get('As_provided_tension', 0):.2f} cm²",
            f"{stirrup_spacing} cm",
            f"{results.get('rho_required', 0):.4f}"
        ],
        'ค่าที่ต้องการ': [
            f"{Mu:,.0f} kg-m",
            f"{Vu:,.0f} kg",
            f"{results.get('As_required', 0):.2f} cm²",
            f"{min((h-cover)/2, 60):.0f} cm",
            f"{results.get('rho_max', 0):.4f}"
        ],
        'ผลการตรวจสอบ': [
            "✅ ผ่าน" if results.get('moment_check', False) else "❌ ไม่ผ่าน",
            "✅ ผ่าน" if results.get('shear_check', False) else "❌ ไม่ผ่าน",
            "✅ ผ่าน" if results.get('tension_steel_adequate', False) else "❌ ไม่ผ่าน",
            "✅ ผ่าน" if results.get('stirrup_adequate', False) else "❌ ไม่ผ่าน",
            "✅ ผ่าน" if results.get('rho_check', False) else "❌ ไม่ผ่าน"
        ]
    }
    
    
    df_check = pd.DataFrame(check_data)
    #st.dataframe(df_check, use_container_width=True, hide_index=True)
    markdown_table = df_check.to_markdown(index=False)
    st.markdown(markdown_table)

    # สรุปเหล็กเสริม
    st.markdown("#### 🔩 สรุปเหล็กเสริมที่เลือก")
    
    steel_summary = {
        'ประเภทเหล็ก': ['เหล็กรับแรงดึง', 'เหล็กรับแรงอัด', 'เหล็กปลอก'],
        'ขนาดและจำนวน': [
            f"{tension_steel_count} เส้น {tension_steel_type}",
            f"{compression_steel_count} เส้น {compression_steel_type}" if compression_steel else '-',
            f"{stirrup_type} {stirrup_legs} ขา @ {stirrup_spacing} cm"
        ],
        'พื้นที่ (cm²)': [
            f"{results.get('As_provided_tension', 0):.2f}",
            f"{results.get('As_prime', 0):.2f}" if compression_steel else '-',
            f"{results.get('Av', 0):.3f}"
        ],
        'สถานะ': [
            "✅ เพียงพอ" if results.get('tension_steel_adequate', False) else "❌ ไม่เพียงพอ",
            "✅ ตามที่เลือก" if compression_steel else '-',
            "✅ เหมาะสม" if results.get('stirrup_adequate', False) else "❌ ไม่เหมาะสม"
        ]
    }
    df_summary = pd.DataFrame(steel_summary)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # กราฟเปรียบเทียบ (ปรับขนาดสำหรับการพิมพ์)
    st.markdown("#### 📊 กราฟเปรียบเทียบ")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # กราฟเปรียบเทียบโมเมนต์ (แนวตั้ง)
        fig_moment = go.Figure()
        fig_moment.add_trace(go.Bar(
            x=['Mu (ใช้งาน)', 'φMn (ต้านทาน)'],
            y=[Mu, results.get('phi_Mn', 0)],
            marker_color=['lightcoral', 'lightgreen'],
            text=[f'{Mu:,.0f}', f"{results.get('phi_Mn', 0):,.0f}"],
            textposition='outside',
            textfont=dict(size=12, color='black')
        ))
        fig_moment.update_layout(
            title=dict(text="เปรียบเทียบโมเมนต์ (kg-m)", font=dict(size=14)),
            yaxis_title="โมเมนต์ (kg-m)",
            xaxis_title="",
            height=250,
            font=dict(size=11),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        fig_moment.update_xaxes(showgrid=False)
        fig_moment.update_yaxes(showgrid=True, gridcolor='lightgray')
        st.plotly_chart(fig_moment, use_container_width=True)
        
    with col2:
        # กราฟเปรียบเทียบแรงเฉือน (แนวตั้ง)
        fig_shear = go.Figure()
        fig_shear.add_trace(go.Bar(
            x=['Vu (ใช้งาน)', 'φVc (ต้านทาน)'],
            y=[Vu, results.get('phi_Vc', 0)],
            marker_color=['lightcoral', 'lightblue'],
            text=[f'{Vu:,.0f}', f"{results.get('phi_Vc', 0):,.0f}"],
            textposition='outside',
            textfont=dict(size=12, color='black')
        ))
        fig_shear.update_layout(
            title=dict(text="เปรียบเทียบแรงเฉือน (kg)", font=dict(size=14)),
            yaxis_title="แรงเฉือน (kg)",
            xaxis_title="",
            height=250,
            font=dict(size=11),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        fig_shear.update_xaxes(showgrid=False)
        fig_shear.update_yaxes(showgrid=True, gridcolor='lightgray')
        st.plotly_chart(fig_shear, use_container_width=True)
    
    # ภาพตัดคาน (ปรับขนาดสำหรับการพิมพ์)
    st.markdown("#### 🏗️ ภาพตัดคาน")
    
    # คำนวณขนาดเหล็กสำหรับการวาด
    steel_sizes_mm = {"DB12": 12, "DB16": 16, "DB20": 20, "DB25": 25, "DB32": 32}
    steel_sizes_mm_stirrup = {"RB6": 6, "RB9": 9, "DB12": 12}
    
    tension_bar_dia = steel_sizes_mm[tension_steel_type]
    stirrup_dia = steel_sizes_mm_stirrup[stirrup_type]
    
    if compression_steel:
        comp_bar_dia = steel_sizes_mm[compression_steel_type]
        beam_fig = draw_beam_section(
            b*10, h*10, cover*10, tension_bar_dia, tension_steel_count, 
            stirrup_dia, stirrup_legs, d_prime*10, comp_bar_dia, compression_steel_count, stirrup_spacing
        )
    else:
        beam_fig = draw_beam_section(
            b*10, h*10, cover*10, tension_bar_dia, tension_steel_count, 
            stirrup_dia, stirrup_legs, stirrup_spacing=stirrup_spacing
        )
    
    # แสดงภาพให้เหมาะกับการพิมพ์
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.pyplot(beam_fig, use_container_width=True)
    
    st.markdown("🔵 เหล็กรับแรงดึง | 🟢 เหล็กรับแรงอัด | 🔴 เหล็กปลอก")
    
    # รายละเอียดการคำนวณ (ต่อท้ายในหน้าเดียวกัน)
    st.markdown("#### 📝 รายละเอียดการคำนวณ")
    
    # แสดงการคำนวณอย่างละเอียดแบบเต็มความกว้าง
    calculations = results.get('calculations', [])
    
    # จัดกลุ่มการคำนวณตามหัวข้อ
    calculation_groups = {}
    current_group = "ข้อมูลทั่วไป"
    current_lines = []
    
    for line in calculations:
        if "===" in line:
            # บันทึกกลุ่มเก่า
            if current_lines:
                calculation_groups[current_group] = current_lines
            # เริ่มกลุ่มใหม่
            current_group = line.replace("===", "").strip()
            current_lines = []
        elif "---" in line and line.strip().startswith("---"):
            # บันทึกกลุ่มเก่า
            if current_lines:
                calculation_groups[current_group] = current_lines
            # เริ่มกลุ่มใหม่
            current_group = line.replace("---", "").strip()
            current_lines = []
        else:
            current_lines.append(line)
    
    # บันทึกกลุ่มสุดท้าย
    if current_lines:
        calculation_groups[current_group] = current_lines
    
    # แสดงการคำนวณทั้งหมด (ไม่ย่อ)
    for group_name, lines in calculation_groups.items():
        if lines and any(line.strip() for line in lines):  # มีข้อมูลจริง
            clean_name = group_name if group_name else "รายละเอียดการคำนวณ"
            
            with st.expander(f"📝 {clean_name}", expanded=True):
                # แสดงข้อมูลในรูปแบบที่อ่านง่าย (ทั้งหมด)
                content = '\n'.join(line for line in lines if line.strip())
                if content:
                    #st.text( content)
                    st.markdown(content)
                    
    
    # สรุปสุดท้าย
    st.markdown("#### 🎯 สรุปผลการออกแบบ")
    
    overall_status = "✅ **ผ่านทุกเงื่อนไข - คานสามารถใช้งานได้**" if results.get('design_ok', False) else "❌ **ไม่ผ่านบางเงื่อนไข - ต้องปรับปรุงการออกแบบ**"
    
    st.markdown(f"""
    <div style="padding: 15px; border: 2px solid {'green' if results.get('design_ok', False) else 'red'}; 
                background-color: {'#e8f5e8' if results.get('design_ok', False) else '#ffeaea'}; 
                border-radius: 10px; text-align: center; font-size: 16px;">
    {overall_status}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # ปิด print-optimized

else:
    # หน้าแรกก่อนกดคำนวณ (ปรับสำหรับการพิมพ์)
    st.markdown('<div class="print-optimized">', unsafe_allow_html=True)
    
    st.info("👈 กรุณากรอกข้อมูลในแถบด้านซ้าย แล้วกดปุ่ม 'คำนวณ' เพื่อดูผลลัพธ์")
    
    # แสดงข้อมูลพื้นฐาน
    st.subheader("📐 ข้อมูลการออกแบบปัจจุบัน")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        **คุณสมบัติวัสดุ:**
        - $f'_c$ = {fc} kg/cm²
        - $f_y$ = {fy} kg/cm²
        """)
        
    with col2:
        st.markdown(f"""
        **ขนาดคาน:**
        - b = {b} cm
        - h = {h} cm
        - d = {h-cover} cm
        - cover = {cover} cm
        """)
        
    with col3:
        st.markdown(f"""
        **แรงกระทำ:**
        - $M_u$ = {Mu:,.0f} kg-m
        - $V_u$ = {Vu:,.0f} kg
        """)
    
    # เหล็กเสริมที่เลือก
    st.subheader("🔩 เหล็กเสริมที่เลือก")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        steel_areas = {'DB12': 1.13, 'DB16': 2.01, 'DB20': 3.14, 'DB25': 4.91, 'DB32': 8.04}
        As_tension_calc = steel_areas[tension_steel_type] * tension_steel_count
        
        st.markdown(f"""
        **เหล็กรับแรงดึง:**
        - {tension_steel_type} จำนวน {tension_steel_count} เส้น
        - $A_s$ = {As_tension_calc:.2f} cm²
        """)
        
        if compression_steel:
            As_prime_calc = steel_areas[compression_steel_type] * compression_steel_count
            st.markdown(f"""
            **เหล็กรับแรงอัด:**
            - {compression_steel_type} จำนวน {compression_steel_count} เส้น
            - As' = {As_prime_calc:.2f} cm²
            - d' = {d_prime} cm
            """)
    
    with col2:
        st.markdown(f"""
        **เหล็กปลอก:**
        - {stirrup_type} จำนวน {stirrup_legs} ขา
        - ระยะเรียง {stirrup_spacing} cm
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ส่วนท้าย
st.markdown("---")
st.caption("🛠️ พัฒนาโดย Sketchup & Civil Engineer | Strength Design Method (SDM) | หน่วย: kg, cm")
