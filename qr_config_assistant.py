"""
QR Configuration Assistant
Module untuk membantu analisis dan konfigurasi QR Code yang optimal.

Author: AI Assistant
Date: July 25, 2025
"""

import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from typing import Dict, List, Tuple, Optional, Any
import json


class QRConfigAssistant:
    """
    Assistant untuk analisis dan optimasi konfigurasi QR Code.
    """
    
    ERROR_CORRECTION_LEVELS = {
        'L': ERROR_CORRECT_L,  # 7%
        'M': ERROR_CORRECT_M,  # 15%
        'Q': ERROR_CORRECT_Q,  # 25%
        'H': ERROR_CORRECT_H   # 30%
    }
    
    ERROR_CORRECTION_PERCENTAGES = {
        'L': 7,
        'M': 15,
        'Q': 25,
        'H': 30
    }
    
    def __init__(self):
        """Initialize QR Configuration Assistant."""
        pass
    
    def analyze_text_requirements(self, text: str) -> Dict[str, Any]:
        """
        Analisis kebutuhan teks untuk QR Code.
        
        Args:
            text (str): Teks yang akan dianalisis
            
        Returns:
            Dict[str, Any]: Hasil analisis teks
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        analysis = {
            'text_length': len(text),
            'character_types': self._analyze_character_types(text),
            'recommended_encoding': self._get_recommended_encoding(text),
            'complexity_score': self._calculate_complexity_score(text)
        }
        
        return analysis
    
    def _analyze_character_types(self, text: str) -> Dict[str, int]:
        """Analisis jenis karakter dalam teks."""
        char_types = {
            'numeric': 0,
            'alphanumeric': 0,
            'special': 0,
            'unicode': 0
        }
        
        for char in text:
            if char.isdigit():
                char_types['numeric'] += 1
            elif char.isalnum():
                char_types['alphanumeric'] += 1
            elif ord(char) < 128:
                char_types['special'] += 1
            else:
                char_types['unicode'] += 1
        
        return char_types
    
    def _get_recommended_encoding(self, text: str) -> str:
        """Menentukan encoding yang direkomendasikan."""
        if text.isdigit():
            return 'numeric'
        elif all(c.isalnum() or c in ' $%*+-./:'for c in text):
            return 'alphanumeric'
        else:
            return 'byte'
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Menghitung skor kompleksitas teks (0-100)."""
        score = 0
        
        # Length factor (longer text = higher complexity)
        length_score = min(len(text) / 100, 1) * 30
        score += length_score
        
        # Character diversity factor
        unique_chars = len(set(text))
        diversity_score = min(unique_chars / 50, 1) * 30
        score += diversity_score
        
        # Special character factor
        special_chars = sum(1 for c in text if not c.isalnum())
        special_score = min(special_chars / 20, 1) * 25
        score += special_score
        
        # Unicode factor
        unicode_chars = sum(1 for c in text if ord(c) > 127)
        unicode_score = min(unicode_chars / 10, 1) * 15
        score += unicode_score
        
        return round(score, 2)
    
    def get_optimal_configuration(self, text: str, priorities: List[str] = None) -> Dict[str, Any]:
        """
        Mendapatkan konfigurasi optimal untuk teks tertentu.
        
        Args:
            text (str): Teks untuk QR Code
            priorities (List[str]): Prioritas optimasi ['size', 'reliability', 'speed']
            
        Returns:
            Dict[str, Any]: Konfigurasi optimal
        """
        if priorities is None:
            priorities = ['reliability', 'size']
        
        text_analysis = self.analyze_text_requirements(text)
        
        # Determine optimal error correction level based on priorities
        if 'reliability' in priorities[:2]:
            error_correction = 'M'  # Balanced
        elif 'size' in priorities[:1]:
            error_correction = 'L'  # Smallest size
        else:
            error_correction = 'Q'  # Higher reliability
        
        # Determine optimal version
        optimal_version = self._find_optimal_version(text, error_correction)
        
        # Determine box size based on complexity
        complexity = text_analysis['complexity_score']
        if complexity < 30:
            box_size = 8
        elif complexity < 60:
            box_size = 10
        else:
            box_size = 12
        
        config = {
            'version': optimal_version,
            'error_correction': error_correction,
            'box_size': box_size,
            'border': 4,
            'encoding': text_analysis['recommended_encoding'],
            'estimated_size': self._estimate_qr_size(optimal_version, box_size, 4),
            'confidence_score': self._calculate_confidence_score(text_analysis, priorities),
            'reasoning': self._generate_reasoning(text_analysis, priorities, error_correction)
        }
        
        return config
    
    def _find_optimal_version(self, text: str, error_correction: str) -> int:
        """Mencari versi QR Code optimal untuk teks."""
        for version in range(1, 41):
            qr = qrcode.QRCode(
                version=version,
                error_correction=self.ERROR_CORRECTION_LEVELS[error_correction],
                box_size=1,
                border=1
            )
            try:
                qr.add_data(text)
                qr.make(fit=True)
                return version
            except:
                continue
        
        raise ValueError("Text too long for QR Code")
    
    def _estimate_qr_size(self, version: int, box_size: int, border: int) -> Tuple[int, int]:
        """Estimasi ukuran QR Code dalam pixels."""
        modules_per_side = 4 * version + 17
        pixel_size = modules_per_side * box_size + 2 * border * box_size
        return (pixel_size, pixel_size)
    
    def _calculate_confidence_score(self, text_analysis: Dict, priorities: List[str]) -> float:
        """Menghitung confidence score untuk konfigurasi."""
        base_score = 70
        
        # Adjust based on text complexity
        complexity = text_analysis['complexity_score']
        if complexity < 30:
            base_score += 20
        elif complexity < 60:
            base_score += 10
        else:
            base_score += 5
        
        # Adjust based on priorities alignment
        if len(priorities) <= 2:
            base_score += 10  # Clear priorities
        
        return min(base_score, 100)
    
    def _generate_reasoning(self, text_analysis: Dict, priorities: List[str], error_correction: str) -> str:
        """Generate reasoning for configuration choice."""
        reasons = []
        
        complexity = text_analysis['complexity_score']
        if complexity < 30:
            reasons.append("Simple text allows for smaller QR size")
        elif complexity > 60:
            reasons.append("Complex text requires larger QR for readability")
        
        if 'reliability' in priorities:
            reasons.append(f"Error correction level {error_correction} chosen for reliability")
        
        if 'size' in priorities:
            reasons.append("Configuration optimized for smaller size")
        
        return "; ".join(reasons) if reasons else "Standard configuration applied"
    
    def compare_configurations(self, text: str, configs: List[Dict]) -> Dict[str, Any]:
        """
        Membandingkan multiple konfigurasi QR Code.
        
        Args:
            text (str): Teks untuk QR Code
            configs (List[Dict]): List konfigurasi untuk dibandingkan
            
        Returns:
            Dict[str, Any]: Hasil perbandingan
        """
        comparison_results = []
        
        for i, config in enumerate(configs):
            try:
                # Generate QR with this config
                qr = qrcode.QRCode(
                    version=config.get('version'),
                    error_correction=self.ERROR_CORRECTION_LEVELS.get(config.get('error_correction', 'M')),
                    box_size=config.get('box_size', 10),
                    border=config.get('border', 4)
                )
                qr.add_data(text)
                qr.make(fit=True)
                
                # Calculate metrics
                size = self._estimate_qr_size(
                    qr.version,
                    config.get('box_size', 10),
                    config.get('border', 4)
                )
                
                result = {
                    'config_index': i,
                    'config': config,
                    'actual_version': qr.version,
                    'estimated_size': size,
                    'error_correction_percentage': self.ERROR_CORRECTION_PERCENTAGES.get(
                        config.get('error_correction', 'M'), 15
                    ),
                    'success': True
                }
                
            except Exception as e:
                result = {
                    'config_index': i,
                    'config': config,
                    'error': str(e),
                    'success': False
                }
            
            comparison_results.append(result)
        
        # Find best configuration
        successful_configs = [r for r in comparison_results if r['success']]
        if successful_configs:
            # Rank by size (smaller is better) and error correction (higher is better)
            best_config = min(successful_configs, key=lambda x: x['estimated_size'][0])
        else:
            best_config = None
        
        return {
            'comparisons': comparison_results,
            'best_config': best_config,
            'recommendation': self._generate_comparison_recommendation(comparison_results)
        }
    
    def _generate_comparison_recommendation(self, results: List[Dict]) -> str:
        """Generate recommendation from comparison results."""
        successful = [r for r in results if r['success']]
        
        if not successful:
            return "No configurations were successful. Try simpler settings."
        
        if len(successful) == 1:
            return "Only one configuration worked successfully."
        
        sizes = [r['estimated_size'][0] for r in successful]
        size_range = max(sizes) - min(sizes)
        
        if size_range < 50:
            return "All configurations produce similar sizes. Choose based on error correction needs."
        else:
            return "Significant size differences found. Consider the smallest viable option."


def create_qr_config_assistant() -> QRConfigAssistant:
    """Factory function untuk membuat QR Config Assistant."""
    return QRConfigAssistant()


# Example usage functions
def analyze_qr_text_simple(text: str) -> Dict[str, Any]:
    """Simple wrapper untuk analisis teks."""
    assistant = create_qr_config_assistant()
    return assistant.analyze_text_requirements(text)


def get_optimal_qr_config(text: str, priorities: List[str] = None) -> Dict[str, Any]:
    """Simple wrapper untuk mendapatkan konfigurasi optimal."""
    assistant = create_qr_config_assistant()
    return assistant.get_optimal_configuration(text, priorities)
