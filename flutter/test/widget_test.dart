import 'package:flutter_test/flutter_test.dart';
import 'package:yot_presentation/models/slide.dart';
import 'package:yot_presentation/models/presentation_file.dart';
import 'package:yot_presentation/services/api_service.dart';

void main() {
  group('Slide model', () {
    test('fromJson parses image slide', () {
      final slide = Slide.fromJson({
        'index': 0,
        'type': 'image',
        'content': 'base64data',
        'title': 'Cover',
      });
      expect(slide.index, 0);
      expect(slide.type, 'image');
      expect(slide.content, 'base64data');
      expect(slide.title, 'Cover');
    });

    test('fromJson handles missing optional fields', () {
      final slide = Slide.fromJson({'index': 1, 'type': 'text'});
      expect(slide.index, 1);
      expect(slide.content, isNull);
      expect(slide.title, isNull);
    });

    test('toJson round-trips correctly', () {
      final slide = Slide(
          index: 2, type: 'text', content: 'Hello', title: 'Intro');
      final json = slide.toJson();
      expect(json['index'], 2);
      expect(json['type'], 'text');
      expect(json['content'], 'Hello');
      expect(json['title'], 'Intro');
    });
  });

  group('PresentationFile model', () {
    test('fromJson parses file_id field', () {
      final f = PresentationFile.fromJson({
        'file_id': 'abc-123',
        'filename': 'deck.pdf',
        'total_slides': 12,
      });
      expect(f.id, 'abc-123');
      expect(f.filename, 'deck.pdf');
      expect(f.totalSlides, 12);
    });

    test('fromJson falls back to id field', () {
      final f = PresentationFile.fromJson({
        'id': 'xyz-456',
        'filename': 'notes.txt',
        'total_slides': 3,
      });
      expect(f.id, 'xyz-456');
    });

    test('fromJson parses thumbnail and createdAt', () {
      final f = PresentationFile.fromJson({
        'file_id': 'thumb-test',
        'filename': 'slides.pdf',
        'total_slides': 5,
        'thumbnail': 'data:image/png;base64,abc123',
        'created_at': '2024-01-01T00:00:00Z',
      });
      expect(f.thumbnail, 'data:image/png;base64,abc123');
      expect(f.createdAt, '2024-01-01T00:00:00Z');
    });

    test('toJson includes thumbnail when present', () {
      final f = PresentationFile(
        id: 'a',
        filename: 'test.pdf',
        totalSlides: 3,
        thumbnail: 'base64data',
      );
      final json = f.toJson();
      expect(json['thumbnail'], 'base64data');
    });

    test('toJson omits thumbnail when null', () {
      final f = PresentationFile(
        id: 'b',
        filename: 'test.pdf',
        totalSlides: 1,
      );
      expect(f.toJson().containsKey('thumbnail'), isFalse);
    });
  });

  group('ApiService base URL normalisation', () {
    test('serverUrl is stored as-is (trailing slash stripping is internal)', () {
      final api = ApiService('http://localhost:5000/');
      // The public field retains the original value; the private _base getter
      // strips the slash internally before building request URIs.
      expect(api.serverUrl, 'http://localhost:5000/');
    });

    test('serverUrl without trailing slash is unchanged', () {
      final api = ApiService('http://192.168.1.10:5000');
      expect(api.serverUrl, 'http://192.168.1.10:5000');
    });
  });
}
